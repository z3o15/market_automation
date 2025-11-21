// 市场自动化工具 - Frida Hook脚本
// 基于传商精灵4.3u的装备市场数据获取和点击事件拦截
// 作者: AI助手
// 功能: 自动点击市场装备并获取装备价格信息

console.log("[+] 市场自动化工具 Frida Hook脚本已启动");

// 配置参数
const CONFIG = {
    // 应用包名
    PACKAGE_NAME: "com.cyjh.elfin",
    
    // 市场API模式匹配
    MARKET_API_PATTERN: /api\/market|equipment|price|item/i,
    
    // 日志级别
    LOG_LEVEL: "INFO", // DEBUG, INFO, WARN, ERROR
    
    // 反检测设置
    ANTI_DETECTION: true,
    
    // 通信文件路径
    COMM_FILE_PATH: "/data/data/com.cyjh.elfin/frida_lua_comm.json",
    
    // 数据缓存大小限制
    MAX_CACHE_SIZE: 1000
};

// 全局变量
let marketDataCache = new Map();
let clickEventQueue = [];
let uiStateCache = new Map();
let isProcessing = false;
let lastActivity = "";
let equipmentListViews = [];

// 日志输出函数
function log(level, message) {
    const levels = ["DEBUG", "INFO", "WARN", "ERROR"];
    const currentLevelIndex = levels.indexOf(CONFIG.LOG_LEVEL);
    const messageLevelIndex = levels.indexOf(level);
    
    if (messageLevelIndex >= currentLevelIndex) {
        const timestamp = new Date().toLocaleString();
        console.log(`[${level}] [MARKET] ${timestamp} - ${message}`);
    }
}

// 1. Hook网络请求拦截市场数据
function hookNetworkRequests() {
    log("INFO", "开始Hook网络请求...");
    
    try {
        // Hook OkHttp3请求
        var OkHttpClient = Java.use("okhttp3.OkHttpClient");
        var Call = Java.use("okhttp3.Call");
        var ResponseBody = Java.use("okhttp3.ResponseBody");
        
        // Hook execute方法（同步请求）
        Call.execute.implementation = function() {
            var request = this.request();
            var url = request.url().toString();
            
            // 检查是否为市场相关API
            if (CONFIG.MARKET_API_PATTERN.test(url)) {
                log("INFO", "拦截市场API请求: " + url);
                
                try {
                    // 记录请求信息
                    var requestInfo = {
                        url: url,
                        method: request.method(),
                        headers: parseHeaders(request.headers()),
                        timestamp: Date.now()
                    };
                    
                    // 执行原始请求
                    var originalResponse = this.execute();
                    var responseBody = originalResponse.body();
                    var responseText = responseBody.string();
                    
                    // 解析市场数据
                    parseMarketData(url, responseText, requestInfo);
                    
                    // 重新创建响应（因为responseBody.string()只能调用一次）
                    var newResponseBody = ResponseBody.create(
                        responseBody.contentType(), 
                        responseText
                    );
                    
                    // 构建新响应
                    var newResponse = originalResponse.newBuilder()
                        .body(newResponseBody)
                        .build();
                    
                    return newResponse;
                } catch (e) {
                    log("ERROR", "处理市场API请求失败: " + e);
                    return this.execute();
                }
            }
            
            return this.execute();
        };
        
        // Hook enqueue方法（异步请求）
        Call.enqueue.implementation = function(responseCallback) {
            var request = this.request();
            var url = request.url().toString();
            
            if (CONFIG.MARKET_API_PATTERN.test(url)) {
                log("INFO", "拦截异步市场API请求: " + url);
                
                // 创建自定义回调拦截器
                var originalCallback = responseCallback;
                var wrappedCallback = Java.registerClass({
                    name: 'MarketCallbackWrapper',
                    implements: [Java.use("okhttp3.Callback")],
                    methods: {
                        onFailure: function(call, e) {
                            log("ERROR", "异步请求失败: " + url + " - " + e.getMessage());
                            originalCallback.onFailure(call, e);
                        },
                        onResponse: function(call, response) {
                            try {
                                var responseBody = response.body();
                                var responseText = responseBody.string();
                                
                                // 解析市场数据
                                parseMarketData(url, responseText, {url: url, async: true});
                                
                                // 重新创建响应
                                var newResponseBody = ResponseBody.create(
                                    responseBody.contentType(), 
                                    responseText
                                );
                                
                                var newResponse = response.newBuilder()
                                    .body(newResponseBody)
                                    .build();
                                
                                originalCallback.onResponse(call, newResponse);
                            } catch (e) {
                                log("ERROR", "处理异步响应失败: " + e);
                                originalCallback.onResponse(call, response);
                            }
                        }
                    }
                });
                
                return this.enqueue(wrappedCallback.$new());
            }
            
            return this.enqueue(responseCallback);
        };
        
        log("INFO", "网络请求Hook成功");
    } catch (e) {
        log("ERROR", "网络请求Hook失败: " + e);
    }
}

// 2. Hook UI点击事件
function hookUIClicks() {
    log("INFO", "开始Hook UI点击事件...");
    
    try {
        var View = Java.use("android.view.View");
        var MotionEvent = Java.use("android.view.MotionEvent");
        
        // Hook performClick方法
        View.performClick.implementation = function() {
            var viewInfo = getViewInfo(this);
            
            // 检测是否为装备相关点击
            if (isEquipmentView(this)) {
                log("INFO", "检测到装备点击: " + JSON.stringify(viewInfo));
                
                // 记录点击事件
                var clickEvent = {
                    timestamp: Date.now(),
                    viewInfo: viewInfo,
                    viewId: getViewId(this),
                    viewText: getViewText(this),
                    bounds: getViewBounds(this),
                    activity: getCurrentActivity()
                };
                
                clickEventQueue.push(clickEvent);
                
                // 限制队列大小
                if (clickEventQueue.length > 100) {
                    clickEventQueue.shift();
                }
                
                // 通知Lua脚本
                notifyLuaScript("equipment_click", clickEvent);
            }
            
            // 添加反检测延迟
            if (CONFIG.ANTI_DETECTION) {
                var delay = Math.floor(Math.random() * 200) + 100;
                Java.use("java.lang.Thread").sleep(delay);
            }
            
            return this.performClick();
        };
        
        // Hook onTouchEvent方法
        View.onTouchEvent.implementation = function(event) {
            var action = event.getAction();
            
            // 记录触摸事件
            if (action === MotionEvent.ACTION_DOWN || action === MotionEvent.ACTION_UP) {
                var viewInfo = getViewInfo(this);
                
                if (isEquipmentView(this)) {
                    var touchEvent = {
                        timestamp: Date.now(),
                        action: action,
                        viewInfo: viewInfo,
                        coordinates: {
                            x: event.getX(),
                            y: event.getY()
                        }
                    };
                    
                    notifyLuaScript("equipment_touch", touchEvent);
                }
            }
            
            return this.onTouchEvent(event);
        };
        
        log("INFO", "UI点击Hook成功");
    } catch (e) {
        log("ERROR", "UI点击Hook失败: " + e);
    }
}

// 3. Hook ListView和RecyclerView以检测装备列表
function hookListViews() {
    log("INFO", "开始Hook列表视图...");
    
    try {
        // Hook ListView
        var ListView = Java.use("android.widget.ListView");
        ListView.setAdapter.implementation = function(adapter) {
            log("DEBUG", "ListView设置适配器");
            
            // 检查是否为装备列表
            if (isEquipmentListView(this)) {
                log("INFO", "检测到装备列表视图");
                equipmentListViews.push(this);
                
                // Hook适配器的getView方法
                hookAdapter(adapter);
            }
            
            return this.setAdapter(adapter);
        };
        
        // Hook RecyclerView
        var RecyclerView = Java.use("androidx.recyclerview.widget.RecyclerView");
        RecyclerView.setAdapter.implementation = function(adapter) {
            log("DEBUG", "RecyclerView设置适配器");
            
            // 检查是否为装备列表
            if (isEquipmentRecyclerView(this)) {
                log("INFO", "检测到装备RecyclerView视图");
                equipmentListViews.push(this);
                
                // Hook RecyclerView的适配器
                hookRecyclerViewAdapter(adapter);
            }
            
            return this.setAdapter(adapter);
        };
        
        log("INFO", "列表视图Hook成功");
    } catch (e) {
        log("ERROR", "列表视图Hook失败: " + e);
    }
}

// 4. Hook Activity变化以监控界面状态
function hookActivityLifecycle() {
    log("INFO", "开始Hook Activity生命周期...");
    
    try {
        var Activity = Java.use("android.app.Activity");
        
        // Hook onResume方法
        Activity.onResume.implementation = function() {
            var activityName = this.getClass().getName();
            lastActivity = activityName;
            
            log("INFO", "Activity进入前台: " + activityName);
            
            // 检查是否为市场界面
            if (isMarketActivity(activityName)) {
                log("INFO", "检测到市场界面，开始扫描装备列表");
                
                // 延迟扫描以确保界面完全加载
                setTimeout(function() {
                    scanEquipmentListViews();
                }, 1000);
            }
            
            return this.onResume();
        };
        
        log("INFO", "Activity生命周期Hook成功");
    } catch (e) {
        log("ERROR", "Activity生命周期Hook失败: " + e);
    }
}

// 5. 解析市场数据
function parseMarketData(url, responseText, requestInfo) {
    try {
        log("DEBUG", "开始解析市场数据...");
        
        var data = JSON.parse(responseText);
        var parsedItems = [];
        
        // 提取装备信息
        if (data.equipment || data.items || data.data || data.list) {
            var equipmentList = data.equipment || data.items || data.data || data.list;
            
            if (Array.isArray(equipmentList)) {
                for (var i = 0; i < equipmentList.length; i++) {
                    var item = equipmentList[i];
                    var equipmentInfo = parseEquipmentItem(item, url);
                    
                    if (equipmentInfo) {
                        parsedItems.push(equipmentInfo);
                        
                        // 存储到缓存
                        var cacheKey = equipmentInfo.id + "_" + equipmentInfo.timestamp;
                        marketDataCache.set(cacheKey, equipmentInfo);
                        
                        log("DEBUG", "解析装备信息: " + JSON.stringify(equipmentInfo));
                    }
                }
            }
        }
        
        // 限制缓存大小
        if (marketDataCache.size > CONFIG.MAX_CACHE_SIZE) {
            var keysToDelete = Array.from(marketDataCache.keys()).slice(0, marketDataCache.size - CONFIG.MAX_CACHE_SIZE);
            keysToDelete.forEach(function(key) {
                marketDataCache.delete(key);
            });
        }
        
        // 通知Lua脚本数据更新
        notifyLuaScript("market_data_update", {
            url: url,
            requestInfo: requestInfo,
            itemCount: parsedItems.length,
            items: parsedItems,
            timestamp: Date.now()
        });
        
        log("INFO", "成功解析 " + parsedItems.length + " 个装备项");
        
    } catch (e) {
        log("ERROR", "解析市场数据失败: " + e);
    }
}

// 6. 工具函数
function getViewInfo(view) {
    try {
        return {
            className: view.getClass().getName(),
            id: view.getId(),
            tag: view.getTag(),
            clickable: view.isClickable(),
            enabled: view.isEnabled(),
            visible: view.getVisibility() === 0, // View.VISIBLE
            bounds: getViewBounds(view)
        };
    } catch (e) {
        return { error: e.message };
    }
}

function getViewBounds(view) {
    try {
        var bounds = Java.use("android.graphics.Rect").$new();
        view.getGlobalVisibleRect(bounds);
        return {
            left: bounds.left(),
            top: bounds.top(),
            right: bounds.right(),
            bottom: bounds.bottom(),
            width: bounds.width(),
            height: bounds.height()
        };
    } catch (e) {
        return null;
    }
}

function isEquipmentView(view) {
    try {
        var viewId = view.getId();
        var viewText = getViewText(view);
        var className = view.getClass().getName();
        var tag = view.getTag();
        
        // 检查视图ID是否包含装备相关标识
        if (viewId && viewId.toString().match(/equipment|item|gear|market/i)) {
            return true;
        }
        
        // 检查视图文本是否包含装备相关内容
        if (viewText && viewText.match(/装备|武器|防具|道具|饰品/i)) {
            return true;
        }
        
        // 检查类名是否为装备相关类型
        if (className && className.match(/Equipment|Item|Gear|Market/i)) {
            return true;
        }
        
        // 检查标签
        if (tag && (tag.toString().match(/equipment|item|gear/i) || 
                   (tag.id && tag.id.toString().match(/equipment|item|gear/i)))) {
            return true;
        }
        
        return false;
    } catch (e) {
        return false;
    }
}

function getViewText(view) {
    try {
        if (view.getClass().getName().indexOf("TextView") !== -1) {
            return view.getText().toString();
        }
        return null;
    } catch (e) {
        return null;
    }
}

function getViewId(view) {
    try {
        var id = view.getId();
        if (id !== 0) {
            return id.toString();
        }
        return null;
    } catch (e) {
        return null;
    }
}

function parseHeaders(headers) {
    try {
        var result = {};
        var size = headers.size();
        
        for (var i = 0; i < size; i++) {
            var name = headers.name(i);
            var value = headers.value(i);
            result[name] = value;
        }
        
        return result;
    } catch (e) {
        return {};
    }
}

function parseEquipmentItem(item, sourceUrl) {
    try {
        return {
            id: item.id || item.itemId || item.uid || generateId(),
            name: item.name || item.title || item.itemName || "",
            price: item.price || item.cost || item.value || 0,
            quality: item.quality || item.rarity || item.grade || "",
            type: item.type || item.category || item.itemType || "",
            level: item.level || item.itemLevel || 0,
            description: item.description || item.desc || "",
            icon: item.icon || item.imageUrl || "",
            attributes: item.attributes || item.stats || {},
            source: sourceUrl,
            timestamp: Date.now()
        };
    } catch (e) {
        log("ERROR", "解析装备项失败: " + e);
        return null;
    }
}

function generateId() {
    return "item_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9);
}

function isEquipmentListView(listView) {
    try {
        // 检查ListView的ID或标签
        var id = listView.getId();
        var tag = listView.getTag();
        
        if (id && id.toString().match(/equipment|item|gear|market/i)) {
            return true;
        }
        
        if (tag && tag.toString().match(/equipment|item|gear|market/i)) {
            return true;
        }
        
        return false;
    } catch (e) {
        return false;
    }
}

function isEquipmentRecyclerView(recyclerView) {
    try {
        // 检查RecyclerView的ID或标签
        var id = recyclerView.getId();
        var tag = recyclerView.getTag();
        
        if (id && id.toString().match(/equipment|item|gear|market/i)) {
            return true;
        }
        
        if (tag && tag.toString().match(/equipment|item|gear|market/i)) {
            return true;
        }
        
        return false;
    } catch (e) {
        return false;
    }
}

function isMarketActivity(activityName) {
    return activityName && activityName.match(/Market|Shop|Store|mall/i);
}

function getCurrentActivity() {
    try {
        var ActivityThread = Java.use("android.app.ActivityThread");
        var currentActivityThread = ActivityThread.currentActivityThread();
        var application = currentActivityThread.getApplication();
        var activityManager = application.getSystemService("activity");
        var runningTasks = activityManager.getRunningTasks(1);
        
        if (runningTasks && runningTasks.size() > 0) {
            var topActivity = runningTasks.get(0).topActivity;
            return topActivity.getClassName();
        }
        
        return lastActivity;
    } catch (e) {
        return lastActivity;
    }
}

function scanEquipmentListViews() {
    try {
        log("DEBUG", "扫描装备列表视图...");
        
        // 遍历已知的装备列表视图
        for (var i = 0; i < equipmentListViews.length; i++) {
            var listView = equipmentListViews[i];
            var items = scanListViewItems(listView);
            
            if (items.length > 0) {
                log("INFO", "在列表视图中发现 " + items.length + " 个装备项");
                notifyLuaScript("equipment_list_scanned", {
                    listView: getViewInfo(listView),
                    items: items,
                    timestamp: Date.now()
                });
            }
        }
    } catch (e) {
        log("ERROR", "扫描装备列表失败: " + e);
    }
}

function scanListViewItems(listView) {
    try {
        var items = [];
        var childCount = listView.getChildCount();
        
        for (var i = 0; i < childCount; i++) {
            var child = listView.getChildAt(i);
            if (child && isEquipmentView(child)) {
                var item = {
                    index: i,
                    view: getViewInfo(child),
                    text: getViewText(child),
                    bounds: getViewBounds(child)
                };
                items.push(item);
            }
        }
        
        return items;
    } catch (e) {
        log("ERROR", "扫描列表项失败: " + e);
        return [];
    }
}

function hookAdapter(adapter) {
    try {
        // Hook BaseAdapter的getView方法
        if (adapter.getClass().getName().indexOf("BaseAdapter") !== -1) {
            adapter.getView.implementation = function(position, convertView, parent) {
                var view = this.getView(position, convertView, parent);
                
                // 检查是否为装备项
                if (isEquipmentView(view)) {
                    log("DEBUG", "发现装备项，位置: " + position);
                }
                
                return view;
            };
        }
    } catch (e) {
        log("ERROR", "Hook适配器失败: " + e);
    }
}

function hookRecyclerViewAdapter(adapter) {
    try {
        // Hook RecyclerView.Adapter的onBindViewHolder方法
        adapter.onBindViewHolder.implementation = function(holder, position) {
            this.onBindViewHolder(holder, position);
            
            try {
                var itemView = holder.itemView;
                if (isEquipmentView(itemView)) {
                    log("DEBUG", "发现RecyclerView装备项，位置: " + position);
                }
            } catch (e) {
                // 忽略错误
            }
        };
    } catch (e) {
        log("ERROR", "Hook RecyclerView适配器失败: " + e);
    }
}

// 7. 与Lua脚本通信
function notifyLuaScript(event, data) {
    try {
        // 通过共享内存或文件系统与Lua脚本通信
        var message = {
            event: event,
            data: data,
            timestamp: Date.now()
        };
        
        // 写入通信文件
        var File = Java.use("java.io.File");
        var FileWriter = Java.use("java.io.FileWriter");
        var commFile = File.$new(CONFIG.COMM_FILE_PATH);
        var fileWriter = FileWriter.$new(commFile, false);
        
        fileWriter.write(JSON.stringify(message));
        fileWriter.close();
        
        log("DEBUG", "已通知Lua脚本: " + event);
        
    } catch (e) {
        log("ERROR", "通知Lua脚本失败: " + e);
    }
}

// 8. 导出函数供Lua调用
rpc.exports = {
    // 获取市场数据
    getMarketData: function() {
        var dataArray = [];
        marketDataCache.forEach(function(value, key) {
            dataArray.push(value);
        });
        return dataArray;
    },
    
    // 获取点击事件
    getClickEvents: function() {
        return clickEventQueue;
    },
    
    // 清除缓存
    clearCache: function() {
        marketDataCache.clear();
        clickEventQueue = [];
        return { success: true };
    },
    
    // 模拟点击
    simulateClick: function(x, y) {
        try {
            var MotionEvent = Java.use("android.view.MotionEvent");
            var SystemClock = Java.use("android.os.SystemClock");
            var Instrumentation = Java.use("android.app.Instrumentation");
            
            var downTime = SystemClock.uptimeMillis();
            var eventTime = SystemClock.uptimeMillis();
            
            var downEvent = MotionEvent.obtain(downTime, eventTime, 
                MotionEvent.ACTION_DOWN, x, y, 0);
            var upEvent = MotionEvent.obtain(downTime, eventTime + 100, 
                MotionEvent.ACTION_UP, x, y, 0);
            
            // 使用Instrumentation注入点击事件
            var instrumentation = Instrumentation.$new();
            instrumentation.sendPointerSync(downEvent);
            instrumentation.sendPointerSync(upEvent);
            
            log("INFO", "模拟点击成功: (" + x + ", " + y + ")");
            return { success: true, x: x, y: y };
        } catch (e) {
            log("ERROR", "模拟点击失败: " + e);
            return { success: false, error: e.message };
        }
    },
    
    // 获取当前界面信息
    getCurrentUI: function() {
        try {
            return {
                activity: getCurrentActivity(),
                equipmentListViews: equipmentListViews.length,
                lastUpdateTime: Date.now()
            };
        } catch (e) {
            return { error: e.message };
        }
    },
    
    // 扫描装备列表
    scanEquipment: function() {
        try {
            scanEquipmentListViews();
            return { success: true };
        } catch (e) {
            return { success: false, error: e.message };
        }
    },
    
    // 设置配置
    setConfig: function(key, value) {
        try {
            CONFIG[key] = value;
            return { success: true };
        } catch (e) {
            return { success: false, error: e.message };
        }
    },
    
    // 获取配置
    getConfig: function(key) {
        try {
            return CONFIG[key];
        } catch (e) {
            return null;
        }
    }
};

// 9. 主函数
function main() {
    log("INFO", "开始执行市场自动化Hook流程...");
    
    Java.perform(function() {
        log("INFO", "Java环境已准备就绪");
        
        // 等待应用完全加载
        setTimeout(function() {
            // 执行各种Hook
            hookNetworkRequests();
            hookUIClicks();
            hookListViews();
            hookActivityLifecycle();
            
            log("INFO", "所有Hook操作完成，市场自动化工具已启动");
            log("INFO", "工具版本: 1.0.0");
            log("INFO", "支持功能: 网络请求拦截、UI点击监控、装备列表扫描");
            
        }, 3000); // 延迟3秒确保应用完全加载
    });
}

// 启动脚本
main();
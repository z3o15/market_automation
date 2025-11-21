# 市场自动化工具

基于传商精灵4.3u的装备市场自动化工具，能够自动点击市场装备并获取装备价格信息。

## 项目简介和概述

市场自动化工具是一个专为传商精灵4.3u应用设计的自动化解决方案，采用Python + Frida + Lua三层架构，实现了装备市场的自动化操作和数据采集。该工具通过Frida Hook技术拦截应用的网络请求和UI事件，结合Lua脚本实现自动化操作流程，最终由Python主程序进行整体控制和数据管理。

### 主要功能

- **自动点击装备**: 模拟人类操作，自动点击市场中的装备项
- **价格数据获取**: 通过Frida Hook拦截网络请求，获取准确的装备价格
- **反检测机制**: 集成多种反检测策略，提高工具稳定性
- **数据统计分析**: 自动生成价格统计报告和分析结果
- **可配置参数**: 丰富的配置选项，适应不同使用场景
- **错误处理**: 完善的错误处理和日志记录系统

## 功能特性列表

### 核心功能
- ✅ 自动化装备市场浏览和点击
- ✅ 实时价格数据采集和分析
- ✅ 多层次反检测机制
- ✅ 可配置的自动化参数
- ✅ 完整的日志记录系统
- ✅ 数据导出和统计报告

### 技术特性
- ✅ Python + Frida + Lua三层架构
- ✅ 动态Hook和脚本注入
- ✅ 多线程数据处理
- ✅ 异常恢复和重试机制
- ✅ 跨平台兼容性

### 安全特性
- ✅ 反调试检测绕过
- ✅ 模拟器检测绕过
- ✅ 人性化操作模拟
- ✅ 随机化延迟和偏移

## 系统要求和依赖

### 系统要求
- **操作系统**: Windows 10/11, Linux, macOS
- **Python版本**: 3.7或更高版本
- **Android版本**: Android 10或更高版本
- **设备要求**: 已启用USB调试的Android设备或模拟器
- **存储空间**: 至少500MB可用空间

### 软件依赖
- **Python包**: 详见requirements.txt
  - frida-tools>=12.0.0
  - psutil>=5.8.0
  - python-dateutil>=2.8.0
  - ujson>=5.0.0
  - colorlog>=6.0.0
  - pyyaml>=6.0
  - requests>=2.25.0
  - pandas>=1.3.0
  - watchdog>=2.1.0
  - pywin32>=304 (仅Windows)

- **Android工具**:
  - Android SDK Platform Tools (包含adb)
  - 传商精灵4.3u APK文件
  - frida-server (与设备架构匹配)

## 安装指南（详细步骤）

### 1. 环境准备

#### 1.1 安装Python环境
```bash
# 下载并安装Python 3.7+ (推荐3.9+)
# 确保pip已安装并更新到最新版本
python -m pip install --upgrade pip
```

#### 1.2 安装项目依赖
```bash
# 克隆或下载项目到本地
cd market_automation

# 安装Python依赖
pip install -r requirements.txt
```

#### 1.3 安装Android SDK
1. 下载Android Studio或Android SDK命令行工具
2. 配置环境变量，确保adb命令可用
3. 验证安装：
```bash
adb version
```

### 2. 设备准备

#### 2.1 启用USB调试
1. 在Android设备上启用"开发者选项"
2. 开启"USB调试"和"USB安装"
3. 连接设备并授权调试

#### 2.2 安装传商精灵4.3u
```bash
# 安装APK文件
adb install 传商精灵4.3u.apk

# 验证安装
adb shell pm list packages | grep com.cyjh.elfin
```

#### 2.3 安装Frida服务器
```bash
# 1. 下载与设备架构匹配的frida-server
# 从 https://github.com/frida/frida/releases 下载

# 2. 推送到设备
adb push frida-server /data/local/tmp/

# 3. 设置执行权限
adb shell chmod +x /data/local/tmp/frida-server

# 4. 启动frida-server (后台运行)
adb shell /data/local/tmp/frida-server -D &
```

### 3. 项目部署

#### 3.1 推送必要文件
```bash
# 创建必要目录
adb shell mkdir -p /data/data/com.cyjh.elfin/scripts
adb shell mkdir -p /data/data/com.cyjh.elfin/data

# 推送脚本文件
adb push scripts/market_hook.js /data/local/tmp/
adb push scripts/market_automation.lua /data/data/com.cyjh.elfin/scripts/

# 推送配置文件
adb push config/lua_config.json /data/data/com.cyjh.elfin/
```

#### 3.2 验证部署
```bash
# 检查文件是否正确推送
adb shell ls -la /data/data/com.cyjh.elfin/scripts/
adb shell ls -la /data/data/com.cyjh.elfin/
adb shell ls -la /data/local/tmp/market_hook.js
```

### 4. 配置验证

#### 4.1 检查Frida连接
```bash
# 列出正在运行的进程
frida-ps -U

# 检查目标应用是否运行
frida-ps -U | grep com.cyjh.elfin
```

#### 4.2 测试脚本注入
```bash
# 测试Frida脚本
frida -U -f com.cyjh.elfin -l /data/local/tmp/market_hook.js --no-pause
```

## 配置说明（各个配置文件的详细解释）

### 1. 主配置文件 (config/market_config.json)

这是项目的主配置文件，包含所有核心功能的配置选项：

```json
{
    "automation": {
        "clickDelay": {
            "min": 300,        // 最小点击延迟(毫秒)
            "max": 800,        // 最大点击延迟(毫秒)
            "default": 500     // 默认点击延迟(毫秒)
        },
        "scrollDelay": {
            "min": 1500,       // 最小滚动延迟(毫秒)
            "max": 2500,       // 最大滚动延迟(毫秒)
            "default": 2000    // 默认滚动延迟(毫秒)
        },
        "maxRetries": 3,           // 最大重试次数
        "retryDelay": 1000,        // 重试延迟(毫秒)
        "scrollInterval": 2000,    // 滚动间隔(毫秒)
        "maxScrollCount": 10,       // 最大滚动次数
        "maxPages": 10,             // 最大浏览页数
        "itemsPerPage": 20,         // 每页项目数
        "pauseBetweenPages": 3000   // 页面间暂停时间(毫秒)
    },
    "market": {
        "apiEndpoints": [           // 市场API端点列表
            "https://api.example.com/market/equipment",
            "https://backup.example.com/market/equipment"
        ],
        "requestTimeout": 10000,        // 请求超时(毫秒)
        "retryInterval": 5000,          // 重试间隔(毫秒)
        "maxConcurrentRequests": 3,     // 最大并发请求数
        "cacheTimeout": 300000,         // 缓存超时(毫秒)
        "refreshInterval": 60000       // 刷新间隔(毫秒)
    },
    "equipment": {
        "targetTypes": [            // 目标装备类型
            "weapon", 
            "armor", 
            "accessory", 
            "consumable"
        ],
        "priceRange": {
            "min": 100,             // 最低价格
            "max": 50000            // 最高价格
        },
        "qualityLevels": [          // 装备品质等级
            "common", 
            "rare", 
            "epic", 
            "legendary"
        ],
        "levelRange": {
            "min": 1,               // 最低等级
            "max": 100              // 最高等级
        },
        "excludeKeywords": [        // 排除关键词
            "破损", 
            "损坏", 
            "过期"
        ],
        "includeKeywords": [        // 包含关键词
            "强化", 
            "精炼", 
            "稀有"
        ]
    },
    "detection": {
        "antiDetection": {
            "randomizeClicks": true,       // 随机化点击
            "humanLikeMovement": true,      // 人类化移动
            "variableTiming": true,        // 可变时间
            "randomScrollSpeed": true,     // 随机滚动速度
            "simulateErrors": false,       // 模拟错误
            "errorRate": 0.05              // 错误率(0-1)
        },
        "stealthMode": true,        // 隐身模式
        "hideRoot": true,           // 隐藏Root
        "hideDebug": true,          // 隐藏调试
        "mimicHumanBehavior": true  // 模拟人类行为
    }
}
```

### 2. Frida配置文件 (config/frida_config.json)

Frida Hook相关的配置选项：

```json
{
    "frida": {
        "scriptPath": "/data/local/tmp/market_hook.js",  // Hook脚本路径
        "packageName": "com.cyjh.elfin",                // 目标应用包名
        "spawn": true,                                   // 是否启动新进程
        "pause": false,                                  // 是否暂停进程
        "runtime": "v8",                                 // 运行时环境
        "enableDebugger": false,                         // 是否启用调试器
        "debuggerPort": 9222                            // 调试器端口
    },
    "hooks": {
        "network": {
            "enabled": true,                     // 启用网络Hook
            "interceptOkHttp": true,             // 拦截OkHttp请求
            "interceptHttpURLConnection": true,  // 拦截HttpURLConnection
            "interceptWebView": false,           // 拦截WebView
            "logRequests": true,                 // 记录请求
            "logResponses": true,                // 记录响应
            "filterPatterns": [                  // 过滤模式
                "api/market",
                "equipment",
                "price",
                "item"
            ]
        },
        "ui": {
            "enabled": true,                     // 启用UI Hook
            "hookClickEvents": true,             // Hook点击事件
            "hookTouchEvents": true,            // Hook触摸事件
            "hookListView": true,               // Hook ListView
            "hookRecyclerView": true,           // Hook RecyclerView
            "hookActivityLifecycle": true,      // Hook Activity生命周期
            "logViewHierarchy": false,          // 记录视图层次
            "logClickCoordinates": true         // 记录点击坐标
        },
        "system": {
            "enabled": false,                    // 启用系统Hook
            "hookFileOperations": false,         // Hook文件操作
            "hookCryptoOperations": false,       // Hook加密操作
            "hookTimeFunctions": false,          // Hook时间函数
            "hookDebugChecks": true              // Hook调试检查
        }
    },
    "antiDetection": {
        "enabled": true,                    // 启用反检测
        "hideFridaTraces": true,            // 隐藏Frida痕迹
        "hideDebugger": true,               // 隐藏调试器
        "bypassAntiDebug": true,            // 绕过反调试
        "bypassEmulatorDetection": true,     // 绕过模拟器检测
        "randomizeTiming": true,            // 随机化时间
        "mimicHumanBehavior": true          // 模拟人类行为
    }
}
```

### 3. Lua配置文件 (config/lua_config.json)

Lua脚本相关的配置选项：

```json
{
    "lua": {
        "scriptPath": "/data/data/com.cyjh.elfin/scripts/market_automation.lua",  // Lua脚本路径
        "autoStart": false,                    // 是否自动启动
        "restartOnError": true,                // 错误时重启
        "maxRestartAttempts": 3,               // 最大重启尝试次数
        "scriptTimeout": 300000                 // 脚本超时(毫秒)
    },
    "communication": {
        "fridaCommFile": "/data/data/com.cyjh.elfin/frida_lua_comm.json",  // 通信文件路径
        "commCheckInterval": 100,              // 通信检查间隔(毫秒)
        "commTimeout": 5000,                    // 通信超时(毫秒)
        "enableRpc": true,                      // 启用RPC
        "rpcPort": 27042                        // RPC端口
    },
    "ui": {
        "marketActivityPatterns": [             // 市场Activity模式
            "MarketActivity",
            "ShopActivity",
            "StoreActivity",
            "MallActivity"
        ],
        "equipmentListIds": [                   // 装备列表视图ID
            "equipment_list_view",
            "market_item_list",
            "item_grid_view"
        ],
        "equipmentItemPatterns": [              // 装备项模式
            "equipment",
            "item",
            "gear",
            "weapon",
            "armor"
        ],
        "priceViewTags": [                      // 价格视图标签
            "item_price",
            "price_tag",
            "cost_label"
        ],
        "nameViewTags": [                       // 名称视图标签
            "item_name",
            "equipment_name",
            "title_text"
        ]
    },
    "automation": {
        "clickDelay": {
            "min": 500,                         // 最小点击延迟(毫秒)
            "max": 1200                          // 最大点击延迟(毫秒)
        },
        "scrollDelay": {
            "min": 1500,                        // 最小滚动延迟(毫秒)
            "max": 2500                          // 最大滚动延迟(毫秒)
        },
        "maxRetries": 3,                        // 最大重试次数
        "retryDelay": 1000,                     // 重试延迟(毫秒)
        "maxPages": 10,                          // 最大页数
        "itemsPerPage": 20,                     // 每页项目数
        "priceRange": {
            "min": 100,                         // 最低价格
            "max": 50000                        // 最高价格
        },
        "targetTypes": [                         // 目标类型
            "weapon",
            "armor",
            "accessory",
            "consumable"
        ]
    }
}
```

## 使用方法（命令行参数和操作示例）

### 1. 基本使用

#### 1.1 启动工具
```bash
# 使用默认配置启动
python main.py --start

# 使用自定义配置启动
python main.py --config /path/to/custom_config.json --start

# 以守护进程模式启动
python main.py --start --daemon

# 启用详细日志
python main.py --start --verbose
```

#### 1.2 工具控制
```bash
# 查看工具状态
python main.py --status

# 暂停工具
python main.py --pause

# 恢复工具
python main.py --resume

# 停止工具
python main.py --stop
```

### 2. 命令行参数详解

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--config` | `-c` | 指定配置文件路径 | `--config /path/to/config.json` |
| `--start` | 无 | 启动工具 | `--start` |
| `--stop` | 无 | 停止工具 | `--stop` |
| `--pause` | 无 | 暂停工具 | `--pause` |
| `--resume` | 无 | 恢复工具 | `--resume` |
| `--status` | 无 | 查看状态 | `--status` |
| `--daemon` | `-d` | 以守护进程模式运行 | `--daemon` |
| `--verbose` | `-v` | 启用详细输出 | `--verbose` |

### 3. 使用示例

#### 3.1 完整工作流程
```bash
# 1. 检查设备连接
adb devices

# 2. 启动frida-server (如果未运行)
adb shell /data/local/tmp/frida-server -D

# 3. 启动市场自动化工具
python main.py --start --verbose

# 4. 查看运行状态
python main.py --status

# 5. 停止工具
python main.py --stop
```

#### 3.2 高级使用场景
```bash
# 场景1: 使用自定义配置并启用详细日志
python main.py --config config/production_config.json --start --verbose

# 场景2: 以守护进程模式运行
python main.py --start --daemon

# 场景3: 运行时暂停和恢复
python main.py --start
python main.py --pause
# ... 进行其他操作 ...
python main.py --resume
python main.py --stop
```

## 项目架构说明

### 1. 整体架构

市场自动化工具采用三层架构设计，各层职责明确：

```
┌─────────────────────────────────────────────────────────────┐
│                    主控制层 (Python)                      │
│  • 整体流程控制  • 配置管理  • 数据处理  • 日志记录        │
├─────────────────────────────────────────────────────────────┤
│                   Frida Hook层 (JavaScript)               │
│  • 网络请求拦截  • UI事件监控  • 数据提取  • 反检测        │
├─────────────────────────────────────────────────────────────┤
│                   Lua脚本层 (Lua)                        │
│  • 自动化操作  • UI交互  • 业务逻辑  • 状态管理          │
├─────────────────────────────────────────────────────────────┤
│                   应用API层 (Android)                     │
│  • 市场界面  • 装备数据  • 网络通信  • 用户交互          │
└─────────────────────────────────────────────────────────────┘
```

### 2. 组件说明

#### 2.1 Python主控制层
- **main.py**: 主控制脚本，负责整体流程管理
- **config_manager.py**: 配置管理器，处理配置文件加载和保存
- **frida_manager.py**: Frida管理器，管理Hook脚本注入和通信
- **lua_manager.py**: Lua管理器，管理Lua脚本执行
- **device_manager.py**: 设备管理器，处理设备连接和文件操作
- **logger.py**: 日志记录器，提供统一的日志接口

#### 2.2 Frida Hook层
- **market_hook.js**: 主要Hook脚本，实现网络请求拦截和UI事件监控
- **网络拦截**: 拦截OkHttp和HttpURLConnection请求，获取市场数据
- **UI监控**: 监控点击事件和触摸事件，跟踪用户交互
- **列表扫描**: 扫描ListView和RecyclerView，识别装备项
- **反检测**: 实现多种反检测机制，提高工具稳定性

#### 2.3 Lua脚本层
- **market_automation.lua**: 主要自动化脚本，实现装备市场操作
- **UI操作**: 实现点击、滚动等UI操作
- **数据处理**: 处理和存储获取到的装备数据
- **状态管理**: 管理自动化流程状态
- **错误处理**: 处理异常情况和重试逻辑

### 3. 数据流程

```
1. Frida Hook拦截网络请求 → 解析市场数据 → 存储到缓存
2. Frida Hook监控UI事件 → 记录用户操作 → 通知Lua脚本
3. Lua脚本执行自动化 → 点击装备项 → 等待数据加载
4. Lua脚本从缓存获取数据 → 处理装备信息 → 存储到数据库
5. Python主控协调各层 → 管理配置 → 生成报告
```

### 4. 通信机制

#### 4.1 Frida与Lua通信
- 通过共享文件系统进行通信
- 通信文件: `/data/data/com.cyjh.elfin/frida_lua_comm.json`
- 支持事件通知和数据交换

#### 4.2 Python与Frida通信
- 使用Frida RPC机制
- 支持方法调用和数据传输
- 提供状态查询和控制接口

## 常见问题解答

### 1. 安装和配置问题

#### Q1: 安装时提示"frida-tools安装失败"
**A**: 这通常是由于网络问题或Python环境配置问题导致的。解决方案：
```bash
# 使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple frida-tools

# 或者升级pip后重试
python -m pip install --upgrade pip
pip install frida-tools
```

#### Q2: 连接设备时提示"设备未找到"
**A**: 检查以下几点：
1. 确保USB调试已启用
2. 检查USB连接线是否正常
3. 确认设备已授权调试
4. 尝试重新连接设备：
```bash
adb kill-server
adb start-server
adb devices
```

#### Q3: frida-server启动失败
**A**: 可能的原因和解决方案：
1. **架构不匹配**: 确保下载的frida-server与设备架构匹配
2. **权限不足**: 确保设置了正确的执行权限
3. **端口占用**: 尝试使用不同的端口或停止占用端口的进程

### 2. 运行时问题

#### Q4: 脚本注入失败
**A**: 检查以下几点：
1. 确保目标应用已安装
2. 检查frida-server是否正常运行
3. 确认脚本文件路径正确
4. 检查应用包名是否正确

#### Q5: 无法获取市场数据
**A**: 可能的原因：
1. **网络问题**: 检查设备网络连接
2. **API变更**: 应用可能更新了API接口
3. **Hook失效**: 可能需要更新Hook脚本
4. **反检测触发**: 应用可能检测到了Hook行为

#### Q6: 自动化操作异常
**A**: 检查以下几点：
1. **UI变化**: 应用界面可能发生了变化
2. **分辨率问题**: 检查设备分辨率配置
3. **性能问题**: 设备性能不足可能导致操作延迟

### 3. 性能和稳定性问题

#### Q7: 工具运行缓慢
**A**: 优化建议：
1. 调整配置中的延迟参数
2. 减少并发请求数量
3. 优化数据缓存设置
4. 检查设备性能和存储空间

#### Q8: 频繁断开连接
**A**: 可能的原因：
1. **USB连接不稳定**: 尝试更换USB线或端口
2. **设备进入休眠**: 调整设备休眠设置
3. **frida-server崩溃**: 检查服务器日志并重启

## 故障排除指南

### 1. 诊断步骤

#### 1.1 基础检查
```bash
# 1. 检查Python环境
python --version
pip list | grep frida

# 2. 检查Android工具
adb version
fastboot version

# 3. 检查设备连接
adb devices
adb shell getprop ro.product.cpu.abi

# 4. 检查frida-server
adb shell ps | grep frida
frida-ps -U
```

#### 1.2 应用状态检查
```bash
# 检查应用是否安装
adb shell pm list packages | grep com.cyjh.elfin

# 检查应用是否运行
adb shell ps | grep com.cyjh.elfin

# 检查应用日志
adb logcat -s com.cyjh.elfin
```

#### 1.3 脚本状态检查
```bash
# 检查脚本文件是否存在
adb shell ls -la /data/local/tmp/market_hook.js
adb shell ls -la /data/data/com.cyjh.elfin/scripts/market_automation.lua

# 检查权限设置
adb shell ls -la /data/local/tmp/frida-server
```

### 2. 常见错误及解决方案

#### 2.1 Frida相关错误

**错误**: `Failed to attach to process: permission denied`
**解决方案**:
```bash
# 重新启动frida-server
adb shell "su -c '/data/local/tmp/frida-server -D'"

# 或者使用root权限
adb shell su -c "/data/local/tmp/frida-server -D"
```

**错误**: `Script failure: unable to locate module`
**解决方案**:
1. 检查目标应用是否正确
2. 确认应用已启动
3. 尝试使用spawn模式启动

#### 2.2 网络相关错误

**错误**: `Network request failed: timeout`
**解决方案**:
1. 检查设备网络连接
2. 调整超时设置
3. 检查API端点是否正确

#### 2.3 UI操作错误

**错误**: `Click operation failed: element not found`
**解决方案**:
1. 检查UI元素标识符
2. 确认界面已完全加载
3. 调整等待时间

### 3. 日志分析

#### 3.1 查看工具日志
```bash
# 实时查看日志
tail -f logs/market_automation.log

# 查看错误日志
grep "ERROR" logs/market_automation.log

# 查看特定时间段日志
grep "2024-01-01 10:" logs/market_automation.log
```

#### 3.2 查看设备日志
```bash
# 查看应用日志
adb logcat -s com.cyjh.elfin

# 查看系统日志
adb logcat | grep -E "(Frida|Market|Hook)"

# 保存日志到文件
adb logcat > device_log.txt
```

#### 3.3 Frida调试
```bash
# 启用详细日志
frida -U -f com.cyjh.elfin -l market_hook.js --no-pause -v

# 使用调试器
frida -U -f com.cyjh.elfin -l market_hook.js --debug
```

### 4. 性能优化

#### 4.1 内存优化
```json
// 在配置文件中调整
{
    "performance": {
        "maxMemoryUsage": 512,      // MB
        "gcInterval": 300000,       // 垃圾回收间隔(毫秒)
        "cacheSize": 1000,          // 缓存大小
        "batchSize": 50             // 批处理大小
    }
}
```

#### 4.2 网络优化
```json
// 在配置文件中调整
{
    "network": {
        "maxConcurrentRequests": 3,     // 减少并发数
        "requestTimeout": 10000,        // 调整超时
        "retryInterval": 5000           // 调整重试间隔
    }
}
```

#### 4.3 UI操作优化
```json
// 在配置文件中调整
{
    "automation": {
        "clickDelay": {
            "min": 500,     // 增加最小延迟
            "max": 1200     // 增加最大延迟
        },
        "scrollDelay": {
            "min": 1500,    // 增加滚动延迟
            "max": 2500
        }
    }
}
```

## 贡献指南

我们欢迎社区贡献！以下是参与项目开发的指南。

### 1. 开发环境设置

#### 1.1 克隆项目
```bash
git clone https://github.com/your-repo/market_automation.git
cd market_automation
```

#### 1.2 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

#### 1.3 安装开发工具
```bash
# 代码格式化工具
pip install black isort flake8

# 测试工具
pip install pytest pytest-cov

# 文档生成工具
pip install sphinx sphinx-rtd-theme
```

### 2. 代码规范

#### 2.1 Python代码规范
- 遵循PEP 8代码风格
- 使用类型注解
- 编写文档字符串
- 保持代码简洁和可读性

```python
# 示例
def process_equipment_data(equipment: Dict[str, Any]) -> bool:
    """处理装备数据
    
    Args:
        equipment: 装备数据字典
        
    Returns:
        bool: 处理是否成功
    """
    try:
        # 实现逻辑
        return True
    except Exception as e:
        logger.error(f"处理装备数据失败: {e}")
        return False
```

#### 2.2 JavaScript代码规范
- 使用ES6+语法
- 保持函数简洁
- 添加适当的注释
- 遵循项目命名约定

```javascript
// 示例
function parseEquipmentData(data) {
    /** 解析装备数据
     * @param {Object} data - 原始数据
     * @returns {Object|null} 解析后的装备数据
     */
    try {
        return {
            id: data.id || '',
            name: data.name || '',
            price: data.price || 0
        };
    } catch (error) {
        console.error(`解析装备数据失败: ${error}`);
        return null;
    }
}
```

#### 2.3 Lua代码规范
- 使用清晰的变量命名
- 添加函数注释
- 保持代码结构清晰
- 处理错误情况

```lua
-- 示例
--- 点击装备项
-- @param item table 装备项数据
-- @return boolean 点击是否成功
function clickEquipmentItem(item)
    if not item then
        log("ERROR", "装备项数据为空")
        return false
    end
    
    -- 实现点击逻辑
    return true
end
```

### 3. 提交流程

#### 3.1 分支管理
1. 从main分支创建功能分支
2. 在功能分支上进行开发
3. 提交前进行测试
4. 创建Pull Request到main分支

```bash
# 创建功能分支
git checkout -b feature/new-feature

# 提交更改
git add .
git commit -m "feat: 添加新功能"

# 推送分支
git push origin feature/new-feature
```

#### 3.2 提交信息规范
使用约定式提交格式：

```
<类型>[可选的作用域]: <描述>

[可选的正文]

[可选的脚注]
```

类型包括：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(automation): 添加装备价格分析功能

- 实现价格趋势分析
- 添加价格统计功能
- 优化数据处理性能

Closes #123
```

### 4. 测试指南

#### 4.1 单元测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_config_manager.py

# 生成覆盖率报告
pytest --cov=utils --cov-report=html
```

#### 4.2 集成测试
```bash
# 运行集成测试
pytest tests/integration/

# 运行端到端测试
pytest tests/e2e/
```

#### 4.3 测试编写示例
```python
# tests/test_config_manager.py
import pytest
from utils.config_manager import ConfigManager

def test_config_manager_load():
    """测试配置管理器加载功能"""
    config_manager = ConfigManager("test_config.json")
    assert config_manager.load_config() == True
    assert config_manager.get("test.key") == "test_value"

def test_config_manager_set():
    """测试配置管理器设置功能"""
    config_manager = ConfigManager("test_config.json")
    assert config_manager.set("new.key", "new_value") == True
    assert config_manager.get("new.key") == "new_value"
```

### 5. 文档贡献

#### 5.1 文档类型
- API文档
- 用户指南
- 开发者文档
- 架构说明

#### 5.2 文档格式
- 使用Markdown格式
- 遵循项目文档结构
- 添加适当的代码示例
- 保持文档更新

#### 5.3 文档提交
```bash
# 更新文档
git add docs/
git commit -m "docs: 更新API文档"
git push origin docs-update
```

### 6. 问题报告

#### 6.1 Bug报告
使用GitHub Issues报告bug，包含以下信息：
- 问题描述
- 复现步骤
- 期望行为
- 实际行为
- 环境信息
- 相关日志

#### 6.2 功能请求
提出新功能建议时，包含：
- 功能描述
- 使用场景
- 预期收益
- 实现建议

### 7. 社区准则

#### 7.1 行为准则
- 尊重他人
- 保持友善
- 接受反馈
- 协作精神

#### 7.2 沟通渠道
- GitHub Issues: 问题报告和功能请求
- GitHub Discussions: 一般讨论
- 邮件列表: 重要公告

感谢您对项目的贡献！您的参与使这个项目变得更好。

---

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 免责声明

本工具仅供学习和研究目的，使用者需要自行承担使用风险。作者不对因使用本工具而产生的任何后果负责。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com
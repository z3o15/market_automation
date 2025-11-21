pip install weditor



# 市场自动化工具 - 简化版使用说明

## 项目概述

这是一个简化版的市场自动化工具，专注于游戏按钮定位和市场装备价格图片获取功能。使用 Python + ADB + UIAutomator2 实现。

## 项目结构

```
market_automation/
├── main.py                          # 主程序入口（核心）
├── requirements.txt                 # 依赖库列表
├── config/
│   └── market_config.json           # 配置文件（简化版）
├── utils/
│   ├── config_manager.py            # 读取配置
│   ├── device_manager.py            # 设备连接（ADB + UIAutomator2）
│   ├── uiautomator2_manager.py      # UIAutomator2 工具类（定位按钮用）
│   ├── file_storage_manager.py      # 保存截图/日志（核心功能）
│   ├── logger.py                    # 日志记录
│   └── interfaces.py               # 接口定义
├── screenshot/
│   └── capture_manager.py           # 截图管理（获取价格图片用）
├── data/
│   ├── screenshots/                 # 存放截图（自动生成）
│   └── logs/                        # 存放日志（自动生成）
└── examples/
    └── basic_usage.py               # 示例脚本（直接运行就能测试）
```

## 快速开始

### 1. 配置 `market_config.json`

打开 `config/market_config.json`，按下面格式修改：

```json
{
  "device": {
    "serial": "127.0.0.1:5557",
    "adb_path": "C:\\Program Files\\Netease\\MuMu\\nx_main\\adb.exe"
  },
  "screenshot": {
    "save_path": "data/screenshots/"
  }
}
```

#### ADB 连接配置说明

1. **获取 MuMu 模拟器 ADB 路径**：
   - MuMu 模拟器默认 ADB 路径：`C:\Program Files\Netease\MuMu\nx_main\adb.exe`
   - 如果安装在其他位置，请相应修改路径

2. **连接 MuMu 模拟器**：
   ```bash
   # 使用 MuMu 自带的 ADB 连接模拟器
   "C:\Program Files\Netease\MuMu\nx_main\adb.exe" connect 127.0.0.1:5557
   
   # 检查连接状态
   "C:\Program Files\Netease\MuMu\nx_main\adb.exe" devices
   ```

3. **配置文件路径格式**：
   - Windows 路径需要使用双反斜杠：`\\`
   - 示例：`"C:\\Program Files\\Netease\\MuMu\\nx_main\\adb.exe"`

### 2. 安装依赖库

```bash
pip install -r requirements.txt
```

如果 `requirements.txt` 里没有 `uiautomator2`，手动补装：

```bash
pip install uiautomator2 pillow  # pillow 是处理图片的
```

### 3. 运行主程序

```bash
python main.py
```

### 4. 运行示例脚本

```bash
python examples/basic_usage.py
```

## 核心功能

### 1. 游戏按钮定位

使用 UIAutomator2 定位游戏中的按钮：

```python
# 通过文本定位按钮
market_btn = u2_manager.find_element_by_text("市场")
if market_btn:
    center = u2_manager.get_element_center(market_btn)
    logger.info(f"找到\"市场\"按钮，坐标：{center}")
    u2_manager.click_element(market_btn)
```

### 2. 市场装备价格图片获取

截取市场界面的价格区域：

```python
# 截全屏
full_screen_path = capture_manager.capture_full_screen(u2_manager.device)
logger.info(f"全屏截图保存成功：{full_screen_path}")

# 截指定区域
price_area_path = capture_manager.capture_region(u2_manager.device, 300, 400, 600, 500)
logger.info(f"价格区域截图保存成功：{price_area_path}")
```

## 使用注意事项

### 1. 设备连接

- 确保 MuMu 模拟器已启动
- 确保已开启 USB 调试（在模拟器设置中）
- 确认 ADB 连接正常：
  ```bash
  # 使用 MuMu 自带的 ADB
  "C:\Program Files\Netease\MuMu\nx_main\adb.exe" devices
  
  # 应该看到类似输出：
  # List of devices attached
  # 127.0.0.1:5557    device
  ```
- 如果使用系统 ADB，确保 MuMu 的 ADB 端口已正确映射

### 2. 按钮定位失败处理

如果游戏是 Unity/Cocos 引擎开发的，按钮是图像（没有文本/ID），按下面步骤处理：

1. 用 ADB 截一张游戏主界面的图：
   ```bash
   adb -s 127.0.0.1:5557 shell screencap -p /sdcard/main_screen.png
   adb -s 127.0.0.1:5557 pull /sdcard/main_screen.png D:\
   ```

2. 用画图工具打开 `main_screen.png`，找到"市场"按钮的中心点坐标

3. 修改代码，用坐标点击：
   ```python
   market_btn_x = 450  # 你的"市场"按钮x坐标
   market_btn_y = 700  # 你的"市场"按钮y坐标
   u2_manager.tap_element(market_btn_x, market_btn_y)
   ```

### 3. 截图路径

- 截图默认保存在 `data/screenshots/` 目录下
- 文件名格式：`时间戳_类型.png`（如 `20231121_154000_full.png`）
- 日志默认保存在 `data/logs/` 目录下

## 常见问题

### 1. ADB 不可用

确保 ADB 路径配置正确：
1. 检查 `config/market_config.json` 中的 `adb_path` 是否正确
2. 确保 MuMu 模拟器已启动并开启 USB 调试
3. 手动执行 ADB 命令测试连接：
   ```bash
   "C:\Program Files\Netease\MuMu\nx_main\adb.exe" devices
   ```
4. 如果使用系统 ADB，确保已添加到系统 PATH 中

### 2. UIAutomator2 初始化失败

确保设备已连接并且已授权 USB 调试。

### 3. 按钮定位失败

- 检查按钮文本是否正确
- 确认按钮是否为图像按钮（无文本）
- 尝试使用坐标定位

## 扩展功能

### 1. 批量截图

```python
# 批量截取多个区域
regions = [(300, 400, 600, 500), (100, 200, 400, 300)]
for i, region in enumerate(regions):
    x1, y1, x2, y2 = region
    path = capture_manager.capture_region(u2_manager.device, x1, y1, x2, y2)
    print(f"区域 {i+1} 截图保存成功：{path}")
```

### 2. 自动化流程

```python
# 自动化流程示例
def automate_market_process():
    # 1. 点击市场按钮
    market_btn = u2_manager.find_element_by_text("市场")
    if market_btn:
        u2_manager.click_element(market_btn)
        time.sleep(2)
        
        # 2. 截图
        capture_manager.capture_full_screen(u2_manager.device)
        
        # 3. 查找装备
        equipment_btn = u2_manager.find_element_by_text("装备")
        if equipment_btn:
            u2_manager.click_element(equipment_btn)
            time.sleep(2)
            
            # 4. 截取装备价格区域
            capture_manager.capture_region(u2_manager.device, 300, 400, 600, 500)
```

## 总结

这个简化版的市场自动化工具专注于核心功能：
1. 游戏按钮定位
2. 市场装备价格图片获取

通过 Python + ADB + UIAutomator2 实现，代码简洁易懂，易于使用和扩展。



# 重要内容
adb connect 127.0.0.1:5557
adb devices
adb -s 127.0.0.1:5557 shell
C:\Program Files\Netease\MuMu\nx_main\adb.exe
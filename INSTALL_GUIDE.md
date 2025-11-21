# 安装指南

## 依赖安装

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 uiautomator2

如果 `requirements.txt` 中没有 `uiautomator2`，手动安装：

```bash
pip install uiautomator2
```

### 3. 安装 Pillow（图像处理）

```bash
pip install pillow
```

## MuMu 模拟器设置

### 1. 启动 MuMu 模拟器

### 2. 开启 USB 调试

1. 在 MuMu 模拟器中，打开"设置"
2. 进入"关于平板电脑"
3. 连续点击"版本号"7次，开启开发者模式
4. 返回"设置"，进入"开发者选项"
5. 开启"USB调试"

### 3. 配置 ADB 连接

1. 打开命令提示符（CMD）或 PowerShell
2. 使用 MuMu 自带的 ADB 连接模拟器：
   ```bash
   "C:\Program Files\Netease\MuMu\nx_main\adb.exe" connect 127.0.0.1:5557
   ```

3. 检查连接状态：
   ```bash
   "C:\Program Files\Netease\MuMu\nx_main\adb.exe" devices
   ```

4. 应该看到类似输出：
   ```
   List of devices attached
   127.0.0.1:5557    device
   ```

## 运行程序

### 1. 运行主程序

```bash
python main.py
```

### 2. 运行示例脚本

```bash
python examples/basic_usage.py
```

## 常见问题

### 1. "No module named 'uiautomator2'"

解决方法：
```bash
pip install uiautomator2
```

### 2. "ADB不可用"

解决方法：
1. 检查 `config/market_config.json` 中的 `adb_path` 是否正确
2. 确保 MuMu 模拟器已启动并开启 USB 调试
3. 手动执行 ADB 命令测试连接：
   ```bash
   "C:\Program Files\Netease\MuMu\nx_main\adb.exe" devices
   ```

### 3. 设备连接失败

解决方法：
1. 确保 MuMu 模拟器已启动
2. 确保 USB 调试已开启
3. 确认 ADB 端口正确（默认为 5557）
4. 尝试重新连接：
   ```bash
   "C:\Program Files\Netease\MuMu\nx_main\adb.exe" disconnect 127.0.0.1:5557
   "C:\Program Files\Netease\MuMu\nx_main\adb.exe" connect 127.0.0.1:5557
   ```

## 项目文件结构

确保你的项目目录包含以下文件：

```
market_automation/
├── main.py                          # 主程序入口
├── requirements.txt                 # 依赖库列表
├── README_SIMPLIFIED.md            # 使用说明
├── INSTALL_GUIDE.md               # 安装指南（本文件）
├── config/
│   └── market_config.json           # 配置文件
├── utils/
│   ├── config_manager.py            # 读取配置
│   ├── device_manager.py            # 设备连接
│   ├── uiautomator2_manager.py      # UIAutomator2 工具类
│   ├── file_storage_manager.py      # 文件存储管理
│   ├── logger.py                    # 日志记录
│   └── interfaces.py               # 接口定义
├── screenshot/
│   ├── __init__.py
│   └── capture_manager.py           # 截图管理
├── data/
│   └── screenshots/                 # 存放截图（自动生成）
└── examples/
    └── basic_usage.py               # 示例脚本
```

## 快速开始

1. 安装依赖：
   ```bash
   pip install uiautomator2 pillow
   ```

2. 配置 ADB 路径（如果需要）：
   编辑 `config/market_config.json`，确保 `adb_path` 正确

3. 连接 MuMu 模拟器：
   ```bash
   "C:\Program Files\Netease\MuMu\nx_main\adb.exe" connect 127.0.0.1:5557
   ```

4. 运行程序：
   ```bash
   python main.py
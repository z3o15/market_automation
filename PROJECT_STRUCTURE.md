# 项目结构说明

## 目录结构

```
market_automation/
├── main.py                    # 主程序入口
├── run_market_automation.py   # 市场自动化运行脚本
├── requirements.txt           # 项目依赖
├── README_SIMPLIFIED.md      # 项目简要说明
├── SCROLL_CONFIG_GUIDE.md    # 滑动配置说明
├── PROJECT_STRUCTURE.md      # 项目结构说明（本文件）
├── config/                   # 配置文件目录
│   └── market_config.json    # 市场自动化配置
├── data/                     # 数据目录
│   └── screenshots/          # 截图保存目录
├── test/                     # 测试文件目录
│   ├── __init__.py          # 测试模块初始化
│   ├── run_tests.py         # 主测试运行器
│   ├── test_screenshot.py   # 截图功能测试
│   ├── test_simple.py       # 简单测试
│   ├── find_button.py       # 按钮查找测试
│   └── find_button_by_image.py # 图像按钮查找测试
├── utils/                    # 工具模块
│   ├── config_manager.py     # 配置管理器
│   ├── logger.py            # 日志记录器
│   ├── uiautomator2_manager.py # UI自动化管理器
│   └── ...                  # 其他工具模块
├── market_automation/        # 市场自动化模块
│   ├── market_clicker.py     # 市场点击器核心功能
│   ├── test_market_clicker.py # 市场点击器测试
│   └── README.md            # 模块说明
├── screenshot/               # 截图模块
│   └── capture_manager.py    # 截图管理器
└── tools/                    # 辅助工具
    └── screen_analyzer.py    # 屏幕分析器
```

## 主要文件说明

### 主程序文件
- **main.py**: 项目主入口，包含程序启动逻辑
- **run_market_automation.py**: 市场自动化运行脚本，可直接执行市场操作

### 配置文件
- **config/market_config.json**: 包含所有市场自动化相关的配置
  - 设备连接配置
  - 按钮坐标配置
  - 滑动距离配置（当前设置为200像素）
  - 等待时间配置

### 核心功能模块
- **market_automation/market_clicker.py**: 市场点击器核心功能
  - 点击市场按钮
  - 点击报价按钮
  - 点击显示全部报价
  - 向上滑动200像素（可配置）
  - 向上滑动800像素（固定）
  - 截图功能
  - 完整的市场操作序列（包含6个步骤）

### 测试文件
- **test/run_tests.py**: 主测试运行器，包含所有测试功能
  - 滑动配置测试（200像素和800像素）
  - 设备连接测试
  - 截图功能测试
  - 800像素滑动功能测试
- **test/test_screenshot.py**: 截图功能专项测试
- 其他测试文件用于特定功能测试

## 使用方法

### 1. 运行市场自动化
```bash
python run_market_automation.py
```

### 2. 运行测试
```bash
# 运行所有测试
python test/run_tests.py

# 只运行截图测试
python test/test_screenshot.py
```

### 3. 修改滑动距离
- **200像素滑动**: 编辑 `config/market_config.json` 中的 `scroll_start` 和 `scroll_end` 配置
- **800像素滑动**: 修改 `market_automation/market_clicker.py` 中 `scroll_up_800_pixels()` 方法的固定坐标

### 4. 查看截图
截图文件保存在 `data/screenshots/` 目录下

## 功能特性

1. **双滑动模式**:
   - 200像素滑动（可配置，适合精确控制）
   - 800像素滑动（固定，适合大幅滚动）
2. **截图功能**: 在每个操作步骤后自动截图
3. **完整操作序列**: 包含6个步骤的市场自动化流程
4. **模块化设计**: 代码结构清晰，易于维护
5. **完整测试**: 提供全面的测试套件

## 注意事项

1. 确保设备已正确连接并配置
2. 运行前检查配置文件中的坐标设置
3. 截图功能需要足够的存储空间
4. 测试时建议先运行连接测试
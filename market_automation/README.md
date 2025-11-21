# 市场自动化点击功能

## 功能概述

市场自动化点击功能模块提供了游戏市场界面的自动化操作，包括：

1. 点击市场按钮 (366, 1204)
2. 点击报价绿色按钮 (320, 445)
3. 点击显示全部报价 (358, 894)
4. 在报价位置向上滑动

## 文件结构

```
market_automation/
├── market_clicker.py      # 市场点击功能核心模块
├── test_market_clicker.py # 测试脚本
├── README.md              # 说明文档
└── market_btn.png         # 市场按钮模板图（可选）
```

## 配置说明

配置文件位于 `config/market_config.json`，包含以下配置项：

```json
{
  "market_automation": {
    "market_button": {
      "x": 366,
      "y": 1204
    },
    "quote_button": {
      "x": 320,
      "y": 445
    },
    "show_all_quotes": {
      "x": 358,
      "y": 894
    },
    "scroll_start": {
      "x": 358,
      "y": 894
    },
    "scroll_end": {
      "x": 358,
      "y": 600
    },
    "after_market_click": 3,
    "after_quote_click": 2,
    "after_show_all": 1,
    "after_scroll": 1
  }
}
```

### 配置项说明

- **坐标配置**：
  - `market_button`: 市场按钮坐标
  - `quote_button`: 报价绿色按钮坐标
  - `show_all_quotes`: 显示全部报价按钮坐标
  - `scroll_start`: 滑动起始位置
  - `scroll_end`: 滑动结束位置

- **等待时间配置**（单位：秒）：
  - `after_market_click`: 点击市场按钮后等待时间
  - `after_quote_click`: 点击报价按钮后等待时间
  - `after_show_all`: 点击显示全部报价后等待时间
  - `after_scroll`: 滑动后等待时间

## 使用方法

### 1. 独立测试

运行测试脚本进行功能测试：

```bash
python market_automation/test_market_clicker.py
```

测试脚本提供两种模式：
- **完整序列测试**：执行完整的市场操作序列
- **单步测试**：逐个测试每个功能

### 2. 集成到主程序

市场点击功能已集成到主程序 `main.py` 中，运行主程序时会自动执行：

```bash
python main.py
```

### 3. 在代码中使用

```python
from market_automation.market_clicker import MarketClicker

# 初始化
market_clicker = MarketClicker(u2_manager, config, logger)

# 执行完整序列
success = market_clicker.execute_market_sequence()

# 或单独执行各个步骤
market_clicker.click_market_button()
market_clicker.click_quote_button()
market_clicker.click_show_all_quotes()
market_clicker.scroll_up_at_quotes_position()
```

## 操作流程

1. **点击市场按钮**：在坐标 (366, 1204) 点击市场按钮，等待3秒
2. **点击报价绿色按钮**：在坐标 (320, 445) 点击报价绿色按钮，等待2秒
3. **点击显示全部报价**：在坐标 (358, 894) 点击显示全部报价，等待1秒
4. **向上滑动**：从 (358, 894) 向上滑动到 (358, 600)，等待1秒

## 注意事项

1. **设备连接**：确保设备已正确连接并配置
2. **游戏状态**：确保游戏已运行并显示在主界面
3. **坐标适配**：如果游戏界面分辨率发生变化，需要调整坐标配置
4. **网络延迟**：根据实际网络情况调整等待时间
5. **权限设置**：确保应用具有必要的辅助功能权限

## 故障排除

### 常见问题

1. **点击无效**：
   - 检查坐标是否正确
   - 确认游戏界面是否显示正常
   - 检查设备连接状态

2. **滑动无效**：
   - 调整滑动起始和结束位置
   - 增加滑动持续时间
   - 检查界面是否可滑动

3. **等待时间不足**：
   - 根据设备性能和网络状况增加等待时间
   - 检查游戏加载速度

### 调试方法

1. 使用 `find_button.py` 查找当前界面可点击元素
2. 使用 `find_button_by_image.py` 通过图像识别定位按钮
3. 查看日志输出了解详细执行过程

## 自定义配置

如需修改坐标或等待时间，编辑 `config/market_config.json` 文件：

```bash
# 编辑配置文件
notepad config/market_config.json
```

修改后重新运行程序即可生效。
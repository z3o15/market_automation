#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找按钮工具
用于查找当前界面上的所有可点击元素，帮助定位目标按钮
"""

import uiautomator2 as u2
import time

def find_buttons():
    """查找当前界面上的所有可点击元素"""
    # 连接模拟器（替换为你的设备ID）
    d = u2.connect("127.0.0.1:5557")
    
    # 获取当前应用信息
    current_app = d.app_current()
    print(f"当前应用：{current_app.get('package')} - {current_app.get('activity')}")
    
    # 截取当前屏幕
    screenshot = d.screenshot()
    if screenshot:
        import os
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"data/screenshots/{timestamp}_button_find.png"
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        screenshot.save(screenshot_path)
        print(f"当前屏幕截图已保存到：{screenshot_path}")
    
    # 确保游戏在前台，等待2秒加载界面
    time.sleep(2)
    
    print("当前界面可点击元素列表（文本+坐标）：")
    print("="*50)
    
    # 遍历所有可点击的元素
    clickable_elements = d.xpath('//*[@clickable="true"]').all()
    print(f"找到 {len(clickable_elements)} 个可点击元素")
    
    for i, elem in enumerate(clickable_elements):
        try:
            # 获取元素信息
            info = elem.info
            text = info.get('text', '').strip()  # 元素文本（按钮上的文字）
            resource_id = info.get('resourceId', '')  # 资源ID
            content_desc = info.get('contentDescription', '').strip()  # 内容描述
            
            # 获取元素中心点坐标
            bounds = info.get("bounds", {})  # 格式：{"left":x1, "top":y1, "right":x2, "bottom":y2}
            x = (bounds.get("left", 0) + bounds.get("right", 0)) // 2
            y = (bounds.get("top", 0) + bounds.get("bottom", 0)) // 2
            
            # 显示元素信息
            if text:
                print(f"{i+1}. 文本：{text} | 坐标：({x}, {y})")
            elif content_desc:
                print(f"{i+1}. 描述：{content_desc} | 坐标：({x}, {y})")
            elif resource_id:
                print(f"{i+1}. ID：{resource_id} | 坐标：({x}, {y})")
            else:
                print(f"{i+1}. 无文本/描述 | 坐标：({x}, {y})")
        except Exception as e:
            print(f"{i+1}. 获取元素信息失败：{e}")
            continue
    
    print("="*50)
    print("提示：找到目标按钮后，直接在脚本中用 d.click(x, y) 点击")

if __name__ == "__main__":
    find_buttons()
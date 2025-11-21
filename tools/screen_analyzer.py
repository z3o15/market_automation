#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
屏幕分析工具
用于分析当前屏幕上的UI元素，帮助定位按钮和控件
"""

import os
import sys
import json
from utils.config_manager import ConfigManager
from utils.device_manager import DeviceManager
from utils.uiautomator2_manager import UIAutomator2Manager
from utils.logger import Logger

# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

def analyze_screen():
    """分析当前屏幕上的UI元素"""
    # 初始化工具
    config = ConfigManager("config/market_config.json")
    logger = Logger()
    device_manager = DeviceManager(config, logger)
    
    # 确认设备连接成功
    if not device_manager.check_device():
        logger.error("设备连接失败！请检查 ADB 和模拟器端口")
        return
    
    # 初始化UIAutomator2管理器
    u2_manager = UIAutomator2Manager(config, logger)
    if not u2_manager.initialize():
        logger.error("UIAutomator2初始化失败")
        return
    
    try:
        # 获取当前应用信息
        current_app = u2_manager.get_current_app()
        if current_app:
            logger.info(f"当前应用：{current_app.get('package')} - {current_app.get('activity')}")
        
        # 获取界面层次结构
        logger.info("获取界面层次结构...")
        hierarchy = u2_manager.dump_hierarchy()
        if hierarchy:
            # 保存层次结构到文件
            with open("data/screenshots/ui_hierarchy.xml", "w", encoding="utf-8") as f:
                f.write(hierarchy)
            logger.info("界面层次结构已保存到：data/screenshots/ui_hierarchy.xml")
        
        # 截取当前屏幕
        logger.info("截取当前屏幕...")
        screenshot_data = u2_manager.take_screenshot()
        if screenshot_data:
            from PIL import Image
            import io
            
            # 保存截图
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"data/screenshots/{timestamp}_analysis.png"
            
            img = Image.open(io.BytesIO(screenshot_data))
            img.save(screenshot_path)
            logger.info(f"当前屏幕截图已保存到：{screenshot_path}")
        
        # 分析可点击的文本元素
        logger.info("分析可点击的文本元素...")
        clickable_texts = []
        
        # 这里需要使用uiautomator2的API来获取所有可点击元素
        # 由于uiautomator2的API限制，我们使用层次结构解析
        if hierarchy:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(hierarchy)
            
            for node in root.iter():
                text = node.attrib.get('text', '')
                clickable = node.attrib.get('clickable', 'false') == 'true'
                resource_id = node.attrib.get('resource-id', '')
                bounds = node.attrib.get('bounds', '')
                
                if clickable and text.strip():
                    clickable_texts.append({
                        'text': text,
                        'resource_id': resource_id,
                        'bounds': bounds
                    })
        
        # 输出结果
        if clickable_texts:
            logger.info("找到以下可点击的文本元素：")
            for i, item in enumerate(clickable_texts[:20]):  # 只显示前20个
                logger.info(f"{i+1}. 文本：'{item['text']}', ID：'{item['resource_id']}', 边界：{item['bounds']}")
            
            # 保存完整结果到JSON文件
            with open("data/screenshots/clickable_elements.json", "w", encoding="utf-8") as f:
                json.dump(clickable_texts, f, ensure_ascii=False, indent=2)
            logger.info(f"完整结果已保存到：data/screenshots/clickable_elements.json")
        else:
            logger.info("未找到可点击的文本元素")
        
        # 提供使用建议
        logger.info("\n使用建议：")
        logger.info("1. 查看 data/screenshots/ui_hierarchy.xml 了解完整的界面结构")
        logger.info("2. 查看 data/screenshots/clickable_elements.json 了解所有可点击元素")
        logger.info("3. 如果找到目标按钮，可以修改 main.py 中的按钮文本")
        logger.info("4. 如果按钮是图像按钮，可以使用坐标定位")
        
    except Exception as e:
        logger.error(f"分析屏幕时发生异常：{str(e)}")
    
    finally:
        # 清理资源
        u2_manager.cleanup()

if __name__ == "__main__":
    import time
    analyze_screen()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图功能测试脚本
测试市场点击器的截图功能
"""

import os
import sys
import time
from datetime import datetime

# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.config_manager import ConfigManager
from utils.logger import Logger
from utils.uiautomator2_manager import UIAutomator2Manager
from market_automation.market_clicker import MarketClicker


def test_screenshot_functionality():
    """测试截图功能"""
    print("=" * 50)
    print("开始测试截图功能")
    print("=" * 50)
    
    # 初始化配置管理器
    config_manager = ConfigManager()
    if not config_manager.initialize():
        print("❌ 配置管理器初始化失败")
        return False
    
    # 初始化日志记录器
    logger = Logger(config_manager)
    if not logger.initialize():
        print("❌ 日志记录器初始化失败")
        return False
    
    # 初始化UIAutomator2管理器
    uiautomator2_manager = UIAutomator2Manager(config_manager, logger)
    if not uiautomator2_manager.initialize():
        print("❌ UIAutomator2管理器初始化失败")
        print("   请确保设备已连接并正确配置")
        return False
    
    # 初始化市场点击器
    market_clicker = MarketClicker(uiautomator2_manager, config_manager, logger)
    if not market_clicker.initialize():
        print("❌ 市场点击器初始化失败")
        return False
    
    try:
        # 测试单独截图功能
        print("\n1. 测试单独截图功能...")
        screenshot_path = market_clicker.take_screenshot("test_single")
        if screenshot_path and os.path.exists(screenshot_path):
            print(f"✅ 单独截图成功：{screenshot_path}")
        else:
            print("❌ 单独截图失败")
            return False
        
        # 测试滑动距离
        print("\n2. 当前滑动配置...")
        coords = market_clicker.coordinates
        start_y = coords['scroll_start']['y']
        end_y = coords['scroll_end']['y']
        distance = abs(start_y - end_y)
        print(f"   滑动起始位置：y = {start_y}")
        print(f"   滑动结束位置：y = {end_y}")
        print(f"   滑动距离：{distance}像素")
        
        if distance == 200:
            print("✅ 滑动距离配置正确（200像素）")
        else:
            print(f"⚠️  滑动距离为{distance}像素，预期为200像素")
        
        # 测试滑动功能（可选）
        print("\n3. 测试滑动功能...")
        user_input = input("是否要测试滑动功能？(y/n): ").lower().strip()
        if user_input == 'y':
            print("   将在3秒后执行滑动...")
            time.sleep(3)
            
            # 滑动前截图
            market_clicker.take_screenshot("before_scroll")
            
            # 执行滑动
            scroll_success = market_clicker.scroll_up_at_quotes_position()
            
            # 滑动后截图
            market_clicker.take_screenshot("after_scroll")
            
            if scroll_success:
                print("✅ 滑动功能测试成功")
            else:
                print("❌ 滑动功能测试失败")
        
        print("\n" + "=" * 50)
        print("截图功能测试完成")
        print("=" * 50)
        print(f"截图文件保存在：{config_manager.get('screenshot', {}).get('save_path', 'data/screenshots/')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常：{str(e)}")
        return False
    
    finally:
        # 清理资源
        try:
            market_clicker.cleanup()
            uiautomator2_manager.cleanup()
            logger.cleanup()
            config_manager.cleanup()
        except:
            pass


if __name__ == "__main__":
    success = test_screenshot_functionality()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行器
统一管理所有测试功能
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


def test_screenshot():
    """测试截图功能"""
    print("\n" + "=" * 50)
    print("测试截图功能")
    print("=" * 50)
    
    # 初始化组件
    config_path = os.path.join(PROJECT_ROOT, "config", "market_config.json")
    config_manager = ConfigManager(config_path)
    
    logger = Logger()
    
    uiautomator2_manager = UIAutomator2Manager(config_manager, logger)
    if not uiautomator2_manager.initialize():
        print("❌ 设备连接失败，跳过截图测试")
        return False
    
    market_clicker = MarketClicker(uiautomator2_manager, config_manager, logger)
    market_clicker.initialize()
    
    try:
        # 测试截图功能
        screenshot_path = market_clicker.take_screenshot("test_main")
        if screenshot_path and os.path.exists(screenshot_path):
            print(f"✅ 截图测试成功：{screenshot_path}")
            return True
        else:
            print("❌ 截图测试失败")
            return False
    except Exception as e:
        print(f"❌ 截图测试异常：{str(e)}")
        return False
    finally:
        market_clicker.cleanup()
        uiautomator2_manager.cleanup()
        # Logger和ConfigManager没有cleanup方法，不需要清理


def test_scroll_800():
    """测试715像素滑动功能"""
    print("\n" + "=" * 50)
    print("测试715像素滑动功能")
    print("=" * 50)
    
    # 初始化组件
    config_path = os.path.join(PROJECT_ROOT, "config", "market_config.json")
    config_manager = ConfigManager(config_path)
    
    logger = Logger()
    
    uiautomator2_manager = UIAutomator2Manager(config_manager, logger)
    if not uiautomator2_manager.initialize():
        print("❌ 设备连接失败，跳过800像素滑动测试")
        return False
    
    market_clicker = MarketClicker(uiautomator2_manager, config_manager, logger)
    market_clicker.initialize()
    
    try:
        # 测试715像素滑动功能
        print("将在3秒后执行715像素滑动测试...")
        time.sleep(3)
        
        # 滑动前截图
        market_clicker.take_screenshot("before_scroll_800")
        
        # 执行800像素滑动
        scroll_success = market_clicker.scroll_up_800_pixels()
        
        # 滑动后截图
        market_clicker.take_screenshot("after_scroll_800_test")
        
        if scroll_success:
            print("✅ 800像素滑动测试成功")
            return True
        else:
            print("❌ 800像素滑动测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 715像素滑动测试异常：{str(e)}")
        return False
    finally:
        market_clicker.cleanup()
        uiautomator2_manager.cleanup()
        # Logger和ConfigManager没有cleanup方法，不需要清理


def test_scroll_config():
    """测试滑动配置"""
    print("\n" + "=" * 50)
    print("测试滑动配置")
    print("=" * 50)
    
    try:
        # 初始化配置管理器
        config_path = os.path.join(PROJECT_ROOT, "config", "market_config.json")
        config_manager = ConfigManager(config_path)
        
        # 创建一个简单的日志记录器用于测试
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("test")
        
        # 初始化市场点击器（不需要设备连接）
        market_clicker = MarketClicker(None, config_manager, logger)
        market_clicker.initialize()
        
        # 检查200像素滑动配置
        coords = market_clicker.coordinates
        start_y = coords['scroll_start']['y']
        end_y = coords['scroll_end']['y']
        distance_200 = abs(start_y - end_y)
        
        print(f"200像素滑动配置：")
        print(f"  滑动起始位置：y = {start_y}")
        print(f"  滑动结束位置：y = {end_y}")
        print(f"  滑动距离：{distance_200}像素")
        
        # 检查800像素滑动配置（固定值）
        scroll_800_start_y, scroll_800_end_y = 900, 100
        distance_800 = abs(scroll_800_start_y - scroll_800_end_y)
        
        print(f"\n800像素滑动配置：")
        print(f"  滑动起始位置：y = {scroll_800_start_y}")
        print(f"  滑动结束位置：y = {scroll_800_end_y}")
        print(f"  滑动距离：{distance_800}像素")
        
        # 验证配置
        success_200 = distance_200 == 200
        success_800 = distance_800 == 800
        
        if success_200:
            print("✅ 200像素滑动配置正确")
        else:
            print(f"⚠️  200像素滑动距离为{distance_200}像素，预期为200像素")
            
        if success_715:
            print("✅ 715像素滑动配置正确")
        else:
            print(f"⚠️  715像素滑动距离为{distance_715}像素，预期为715像素")
        
        return success_200 and success_715
            
    except Exception as e:
        print(f"❌ 滑动配置测试异常：{str(e)}")
        return False
    finally:
        try:
            market_clicker.cleanup()
            # ConfigManager没有cleanup方法，不需要清理
        except:
            pass


def test_device_connection():
    """测试设备连接"""
    print("\n" + "=" * 50)
    print("测试设备连接")
    print("=" * 50)
    
    try:
        # 初始化组件
        config_path = os.path.join(PROJECT_ROOT, "config", "market_config.json")
        config_manager = ConfigManager(config_path)
        
        logger = Logger()
        
        uiautomator2_manager = UIAutomator2Manager(config_manager, logger)
        
        if uiautomator2_manager.initialize():
            device_info = uiautomator2_manager.get_device_info()
            if device_info:
                print(f"✅ 设备连接成功")
                print(f"   设备型号：{device_info.get('brand', 'Unknown')} {device_info.get('model', 'Unknown')}")
                print(f"   屏幕分辨率：{device_info.get('width', 0)}x{device_info.get('height', 0)}")
                print(f"   系统版本：Android {device_info.get('version', 'Unknown')}")
                return True
            else:
                print("❌ 无法获取设备信息")
                return False
        else:
            print("❌ 设备连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 设备连接测试异常：{str(e)}")
        return False
    finally:
        try:
            uiautomator2_manager.cleanup()
            # Logger和ConfigManager没有cleanup方法，不需要清理
        except:
            pass


def main():
    """主测试函数"""
    print("市场自动化测试套件")
    print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # 测试1：滑动配置
    test_results.append(("滑动配置", test_scroll_config()))
    
    # 测试2：设备连接
    test_results.append(("设备连接", test_device_connection()))
    
    # 测试3：截图功能（需要设备连接）
    test_results.append(("截图功能", test_screenshot()))
    
    # 测试4：715像素滑动功能（需要设备连接）
    test_results.append(("715像素滑动", test_scroll_800()))
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:12} : {status}")
        if result:
            passed += 1
    
    print(f"\n总计：{passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return True
    else:
        print("⚠️  部分测试失败，请检查配置和设备连接")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
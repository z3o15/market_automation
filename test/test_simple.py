#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本
验证市场自动化功能的基本导入和初始化
"""

import sys
import os

# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        # 测试基础工具模块
        from utils.config_manager import ConfigManager
        from utils.logger import Logger
        from utils.uiautomator2_manager import UIAutomator2Manager
        print("✅ 基础工具模块导入成功")
        
        # 测试市场自动化模块
        from market_automation.market_clicker import MarketClicker
        print("✅ 市场点击模块导入成功")
        
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败：{str(e)}")
        return False

def test_config():
    """测试配置加载"""
    print("\n测试配置加载...")
    
    try:
        from utils.config_manager import ConfigManager
        config = ConfigManager("config/market_config.json")
        
        # 检查市场自动化配置
        market_config = config.get('market_automation', {})
        if market_config:
            print("✅ 市场自动化配置加载成功")
            print(f"   市场按钮坐标：{market_config.get('market_button', {})}")
            print(f"   报价按钮坐标：{market_config.get('quote_button', {})}")
            return True
        else:
            print("❌ 市场自动化配置为空")
            return False
    except Exception as e:
        print(f"❌ 配置加载失败：{str(e)}")
        return False

def test_market_clicker_init():
    """测试市场点击器初始化"""
    print("\n测试市场点击器初始化...")
    
    try:
        from utils.config_manager import ConfigManager
        from utils.logger import Logger
        from market_automation.market_clicker import MarketClicker
        
        config = ConfigManager("config/market_config.json")
        logger = Logger()
        
        # 创建模拟的u2_manager对象用于测试
        class MockU2Manager:
            def __init__(self):
                self.is_connected = True
        
        mock_u2 = MockU2Manager()
        market_clicker = MarketClicker(mock_u2, config, logger)
        
        # 测试初始化方法
        if market_clicker.initialize():
            print("✅ 市场点击器初始化成功")
            print(f"   坐标配置：{market_clicker.coordinates}")
            print(f"   等待时间配置：{market_clicker.wait_times}")
            
            # 测试清理方法
            if market_clicker.cleanup():
                print("✅ 市场点击器清理成功")
            else:
                print("❌ 市场点击器清理失败")
                return False
            
            return True
        else:
            print("❌ 市场点击器初始化失败")
            return False
    except Exception as e:
        print(f"❌ 市场点击器初始化失败：{str(e)}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("市场自动化功能 - 基础测试")
    print("=" * 60)
    
    tests = [
        ("模块导入测试", test_imports),
        ("配置加载测试", test_config),
        ("市场点击器初始化测试", test_market_clicker_init)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} 失败")
    
    print(f"\n{'='*60}")
    print(f"测试结果：{passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有基础测试通过！可以运行完整功能测试。")
        print("\n运行方式：")
        print("1. 完整测试：python market_automation/test_market_clicker.py")
        print("2. 便捷运行：python run_market_automation.py")
        print("3. 主程序：python main.py")
    else:
        print("❌ 部分测试失败，请检查配置和依赖。")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
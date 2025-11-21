#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市场点击功能测试脚本
独立运行测试市场自动化点击功能
"""

import sys
import os
import time

# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.config_manager import ConfigManager
from utils.logger import Logger
from utils.uiautomator2_manager import UIAutomator2Manager
from market_clicker import MarketClicker


def test_market_clicker():
    """测试市场点击功能"""
    print("=" * 60)
    print("市场点击功能测试")
    print("=" * 60)
    
    # 1. 初始化配置和日志
    config = ConfigManager("config/market_config.json")
    logger = Logger()
    
    # 2. 初始化UIAutomator2管理器
    u2_manager = UIAutomator2Manager(config, logger)
    if not u2_manager.initialize():
        logger.error("UIAutomator2初始化失败")
        return False
    
    # 3. 初始化市场点击器
    market_clicker = MarketClicker(u2_manager, config, logger)
    if not market_clicker.initialize():
        logger.error("市场点击器初始化失败")
        return False
    
    try:
        # 4. 显示当前配置
        print("\n当前配置：")
        print(f"市场按钮坐标：{market_clicker.coordinates['market_button']}")
        print(f"报价按钮坐标：{market_clicker.coordinates['quote_button']}")
        print(f"显示全部报价坐标：{market_clicker.coordinates['show_all_quotes']}")
        print(f"滑动起始位置：{market_clicker.coordinates['scroll_start']}")
        print(f"滑动结束位置：{market_clicker.coordinates['scroll_end']}")
        
        print("\n等待时间配置：")
        print(f"点击市场后等待：{market_clicker.wait_times['after_market_click']}秒")
        print(f"点击报价后等待：{market_clicker.wait_times['after_quote_click']}秒")
        print(f"显示全部报价后等待：{market_clicker.wait_times['after_show_all']}秒")
        print(f"滑动后等待：{market_clicker.wait_times['after_scroll']}秒")
        
        # 5. 询问用户是否开始测试
        print("\n" + "=" * 60)
        print("请确保游戏已运行并显示在主界面")
        print("按 Enter 键开始测试，或输入 'q' 退出...")
        user_input = input().strip()
        if user_input.lower() == 'q':
            print("测试取消")
            return False
        
        # 6. 执行完整的市场操作序列
        print("\n开始执行市场操作序列...")
        success = market_clicker.execute_market_sequence()
        
        if success:
            print("\n✅ 市场操作序列执行成功！")
            return True
        else:
            print("\n❌ 市场操作序列执行失败！")
            return False
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断测试")
        return False
    except Exception as e:
        logger.error(f"测试过程中发生异常：{str(e)}")
        print(f"\n❌ 测试异常：{str(e)}")
        return False
    finally:
        # 7. 清理资源
        u2_manager.cleanup()
        print("\n测试完成，资源已清理")


def test_individual_steps():
    """测试单个步骤"""
    print("=" * 60)
    print("市场点击功能 - 单步测试")
    print("=" * 60)
    
    # 1. 初始化配置和日志
    config = ConfigManager("config/market_config.json")
    logger = Logger()
    
    # 2. 初始化UIAutomator2管理器
    u2_manager = UIAutomator2Manager(config, logger)
    if not u2_manager.initialize():
        logger.error("UIAutomator2初始化失败")
        return False
    
    # 3. 初始化市场点击器
    market_clicker = MarketClicker(u2_manager, config, logger)
    if not market_clicker.initialize():
        logger.error("市场点击器初始化失败")
        return False
    
    try:
        while True:
            print("\n请选择要测试的功能：")
            print("1. 点击市场按钮 (366, 1204)")
            print("2. 点击报价绿色按钮 (320, 445)")
            print("3. 点击显示全部报价 (358, 894)")
            print("4. 向上滑动")
            print("0. 退出")
            
            choice = input("请输入选择 (0-4): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                print("\n执行：点击市场按钮")
                market_clicker.click_market_button()
            elif choice == '2':
                print("\n执行：点击报价绿色按钮")
                market_clicker.click_quote_button()
            elif choice == '3':
                print("\n执行：点击显示全部报价")
                market_clicker.click_show_all_quotes()
            elif choice == '4':
                print("\n执行：向上滑动")
                market_clicker.scroll_up_at_quotes_position()
            else:
                print("无效选择，请重新输入")
                
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断测试")
    except Exception as e:
        logger.error(f"测试过程中发生异常：{str(e)}")
        print(f"\n❌ 测试异常：{str(e)}")
    finally:
        # 清理资源
        if 'market_clicker' in locals():
            market_clicker.cleanup()
        u2_manager.cleanup()
        print("\n测试完成，资源已清理")


if __name__ == "__main__":
    print("市场点击功能测试程序")
    print("1. 完整序列测试")
    print("2. 单步测试")
    
    mode = input("请选择测试模式 (1-2): ").strip()
    
    if mode == '1':
        test_market_clicker()
    elif mode == '2':
        test_individual_steps()
    else:
        print("无效选择")
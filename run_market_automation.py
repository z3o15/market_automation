#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市场自动化功能运行脚本
提供简单的方式来运行市场点击功能
"""

import sys
import os

# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# 导入测试函数
sys.path.append(os.path.join(PROJECT_ROOT, 'market_automation'))
from test_market_clicker import test_market_clicker, test_individual_steps


def main():
    """主函数"""
    print("=" * 60)
    print("市场自动化功能运行程序")
    print("=" * 60)
    
    print("请选择运行模式：")
    print("1. 完整序列测试")
    print("2. 单步测试")
    print("3. 运行主程序（包含市场自动化）")
    print("0. 退出")
    
    while True:
        choice = input("\n请输入选择 (0-3): ").strip()
        
        if choice == '0':
            print("程序退出")
            break
        elif choice == '1':
            print("\n开始完整序列测试...")
            test_market_clicker()
            break
        elif choice == '2':
            print("\n开始单步测试...")
            test_individual_steps()
            break
        elif choice == '3':
            print("\n运行主程序...")
            try:
                from main import main as main_func
                main_func()
            except Exception as e:
                print(f"运行主程序时发生错误：{str(e)}")
            break
        else:
            print("无效选择，请重新输入")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础使用示例
演示如何使用简化版的市场自动化工具进行游戏按钮定位和市场装备价格图片获取
"""

import os
import sys
import time

# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.config_manager import ConfigManager
from utils.device_manager import DeviceManager
from utils.uiautomator2_manager import UIAutomator2Manager
from utils.logger import Logger

class SimpleCaptureManager:
    """简化的截图管理器"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.save_path = config.get("screenshot", {}).get("save_path", "data/screenshots/")
        
        # 确保目录存在
        os.makedirs(self.save_path, exist_ok=True)
    
    def capture_full_screen(self, device):
        """截取全屏"""
        try:
            # 使用UIAutomator2截图
            screenshot_data = device.screenshot()
            if screenshot_data:
                # 生成文件名
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_full.png"
                filepath = os.path.join(self.save_path, filename)
                
                # 保存截图
                screenshot_data.save(filepath)
                self.logger.info(f"全屏截图保存成功：{filepath}")
                return filepath
            else:
                self.logger.error("截图失败")
                return None
        except Exception as e:
            self.logger.error(f"截图异常：{str(e)}")
            return None
    
    def capture_region(self, device, x1, y1, x2, y2):
        """截取指定区域"""
        try:
            # 先截取全屏
            screenshot_data = device.screenshot()
            if screenshot_data:
                # 裁剪指定区域
                region = screenshot_data.crop((x1, y1, x2, y2))
                
                # 生成文件名
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_region_{x1}_{y1}_{x2}_{y2}.png"
                filepath = os.path.join(self.save_path, filename)
                
                # 保存截图
                region.save(filepath)
                self.logger.info(f"区域截图保存成功：{filepath}")
                return filepath
            else:
                self.logger.error("截图失败")
                return None
        except Exception as e:
            self.logger.error(f"区域截图异常：{str(e)}")
            return None

def test_device_connection():
    """测试设备连接"""
    print("=== 测试设备连接 ===")
    
    # 初始化配置和日志
    config = ConfigManager("config/market_config.json")
    logger = Logger()
    device_manager = DeviceManager(config, logger)
    
    # 检查设备连接
    if device_manager.check_device():
        print(f"✓ 设备连接成功：{device_manager.device_id}")
        return device_manager
    else:
        print("✗ 设备连接失败！请检查 ADB 和模拟器端口")
        return None

def test_uiautomator2(device_manager):
    """测试UIAutomator2功能"""
    print("\n=== 测试UIAutomator2功能 ===")
    
    config = ConfigManager("config/market_config.json")
    logger = Logger()
    
    # 初始化UIAutomator2管理器
    u2_manager = UIAutomator2Manager(config, logger)
    if not u2_manager.initialize():
        print("✗ UIAutomator2初始化失败")
        return None
    
    print("✓ UIAutomator2初始化成功")
    
    # 获取设备信息
    device_info = u2_manager.get_device_info()
    if device_info:
        print(f"✓ 设备信息：{device_info['brand']} {device_info['model']}")
        print(f"✓ 屏幕分辨率：{device_info['width']}x{device_info['height']}")
    
    return u2_manager

def test_screenshot(u2_manager):
    """测试截图功能"""
    print("\n=== 测试截图功能 ===")
    
    config = ConfigManager("config/market_config.json")
    logger = Logger()
    
    # 初始化截图管理器
    capture_manager = SimpleCaptureManager(config.config, logger)
    
    # 截取全屏
    print("正在截取全屏...")
    full_screen_path = capture_manager.capture_full_screen(u2_manager.device)
    if full_screen_path:
        print(f"✓ 全屏截图保存成功：{full_screen_path}")
    else:
        print("✗ 全屏截图失败")
        return None
    
    # 截取指定区域（示例：屏幕中央区域）
    device_info = u2_manager.get_device_info()
    if device_info:
        width = device_info['width']
        height = device_info['height']
        
        # 计算中央区域
        x1 = width // 4
        y1 = height // 4
        x2 = width * 3 // 4
        y2 = height * 3 // 4
        
        print(f"正在截取区域：({x1}, {y1}) 到 ({x2}, {y2})")
        region_path = capture_manager.capture_region(u2_manager.device, x1, y1, x2, y2)
        if region_path:
            print(f"✓ 区域截图保存成功：{region_path}")
        else:
            print("✗ 区域截图失败")
    
    return capture_manager

def test_button_location(u2_manager):
    """测试按钮定位功能"""
    print("\n=== 测试按钮定位功能 ===")
    
    # 尝试查找常见的游戏按钮
    common_buttons = ["市场", "背包", "任务", "商城", "商店", "shop", "market"]
    
    for button_text in common_buttons:
        print(f"正在查找按钮：{button_text}")
        button = u2_manager.find_element_by_text(button_text)
        if button:
            center = u2_manager.get_element_center(button)
            print(f"✓ 找到按钮：{button_text}，坐标：{center}")
            
            # 询问是否点击
            # 注意：在实际使用中，你可能不想自动点击，这里只是演示
            # u2_manager.click_element(button)
            # print(f"✓ 已点击按钮：{button_text}")
            return button
        else:
            print(f"✗ 未找到按钮：{button_text}")
    
    print("未找到任何常见按钮，可能需要使用坐标定位")
    return None

def test_coordinate_click(u2_manager):
    """测试坐标点击功能"""
    print("\n=== 测试坐标点击功能 ===")
    
    # 获取屏幕尺寸
    device_info = u2_manager.get_device_info()
    if not device_info:
        print("✗ 无法获取设备信息")
        return
    
    width = device_info['width']
    height = device_info['height']
    
    # 点击屏幕中央（安全区域）
    center_x = width // 2
    center_y = height // 2
    
    print(f"正在点击坐标：({center_x}, {center_y})")
    if u2_manager.tap_element(center_x, center_y):
        print(f"✓ 成功点击坐标：({center_x}, {center_y})")
    else:
        print(f"✗ 点击坐标失败：({center_x}, {center_y})")

def main():
    """主函数"""
    print("市场自动化工具 - 基础使用示例")
    print("=" * 50)
    
    # 1. 测试设备连接
    device_manager = test_device_connection()
    if not device_manager:
        return
    
    # 2. 测试UIAutomator2
    u2_manager = test_uiautomator2(device_manager)
    if not u2_manager:
        return
    
    # 3. 测试截图功能
    capture_manager = test_screenshot(u2_manager)
    
    # 4. 测试按钮定位
    button = test_button_location(u2_manager)
    
    # 5. 测试坐标点击
    test_coordinate_click(u2_manager)
    
    # 清理资源
    u2_manager.cleanup()
    
    print("\n=== 测试完成 ===")
    print("截图文件保存在：data/screenshots/ 目录下")
    print("如果按钮定位失败，请检查游戏界面或使用坐标定位")

if __name__ == "__main__":
    main()
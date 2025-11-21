#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市场点击功能模块
实现游戏市场界面的自动化点击操作
"""

import time
import sys
import os
from typing import Optional, Dict, Any

# 添加项目根目录到Python路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.interfaces import BaseModule
from utils.logger import Logger


class MarketClicker(BaseModule):
    """市场点击功能类"""
    
    def __init__(self, uiautomator2_manager, config_manager, logger):
        """初始化市场点击器
        
        Args:
            uiautomator2_manager: UIAutomator2管理器实例
            config_manager: 配置管理器实例
            logger: 日志记录器实例
        """
        super().__init__(config_manager, logger)
        self.u2_manager = uiautomator2_manager
        self.config = self.config_manager.get('market_automation', {})
        
        # 默认坐标配置
        self.coordinates = {
            'market_button': self.config.get('market_button', {'x': 366, 'y': 1204}),
            'quote_button': self.config.get('quote_button', {'x': 320, 'y': 445}),
            'show_all_quotes': self.config.get('show_all_quotes', {'x': 358, 'y': 894}),
            'scroll_start': self.config.get('scroll_start', {'x': 358, 'y': 894}),
            'scroll_end': self.config.get('scroll_end', {'x': 358, 'y': 600})
        }
        
        # 默认等待时间配置（秒）
        self.wait_times = {
            'after_market_click': self.config.get('after_market_click', 3),
            'after_quote_click': self.config.get('after_quote_click', 2),
            'after_show_all': self.config.get('after_show_all', 1),
            'after_scroll': self.config.get('after_scroll', 1)
        }
    
    def click_market_button(self) -> bool:
        """点击市场按钮 (366, 1204)
        
        Returns:
            bool: 操作是否成功
        """
        try:
            coords = self.coordinates['market_button']
            self.logger.info(f"点击市场按钮，坐标：({coords['x']}, {coords['y']})")
            
            success = self.u2_manager.tap_element(coords['x'], coords['y'])
            if success:
                self.logger.info("市场按钮点击成功")
                time.sleep(self.wait_times['after_market_click'])
                return True
            else:
                self.logger.error("市场按钮点击失败")
                return False
                
        except Exception as e:
            self.logger.error(f"点击市场按钮异常：{str(e)}")
            return False
    
    def click_quote_button(self) -> bool:
        """点击报价绿色按钮 (320, 445)
        
        Returns:
            bool: 操作是否成功
        """
        try:
            coords = self.coordinates['quote_button']
            self.logger.info(f"点击报价绿色按钮，坐标：({coords['x']}, {coords['y']})")
            
            success = self.u2_manager.tap_element(coords['x'], coords['y'])
            if success:
                self.logger.info("报价绿色按钮点击成功")
                time.sleep(self.wait_times['after_quote_click'])
                return True
            else:
                self.logger.error("报价绿色按钮点击失败")
                return False
                
        except Exception as e:
            self.logger.error(f"点击报价绿色按钮异常：{str(e)}")
            return False
    
    def click_show_all_quotes(self) -> bool:
        """点击显示全部报价 (358, 894)
        
        Returns:
            bool: 操作是否成功
        """
        try:
            coords = self.coordinates['show_all_quotes']
            self.logger.info(f"点击显示全部报价，坐标：({coords['x']}, {coords['y']})")
            
            success = self.u2_manager.tap_element(coords['x'], coords['y'])
            if success:
                self.logger.info("显示全部报价点击成功")
                time.sleep(self.wait_times['after_show_all'])
                return True
            else:
                self.logger.error("显示全部报价点击失败")
                return False
                
        except Exception as e:
            self.logger.error(f"点击显示全部报价异常：{str(e)}")
            return False
    
    def scroll_up_at_quotes_position(self) -> bool:
        """在显示全部报价位置向上滑动
        
        滑动距离说明：
        - 起始位置：scroll_start (当前 y: 900)
        - 结束位置：scroll_end (当前 y: 700)
        - 滑动距离：900 - 700 = 200 像素（适合精确控制）
        - 滑动持续时间：500毫秒
        
        修改滑动距离的方法：
        1. 推荐：修改 config/market_config.json 中的 scroll_start 和 scroll_end 坐标
        2. 或者：修改下方 self.coordinates 中的默认值
        
        Returns:
            bool: 操作是否成功
        """
        try:
            # 获取滑动起始和结束坐标
            start_coords = self.coordinates['scroll_start']
            end_coords = self.coordinates['scroll_end']
            
            # 计算实际滑动距离（用于日志显示）
            scroll_distance = abs(start_coords['y'] - end_coords['y'])
            
            self.logger.info(f"在报价位置向上滑动，从({start_coords['x']}, {start_coords['y']})到({end_coords['x']}, {end_coords['y']})")
            self.logger.info(f"滑动距离：{scroll_distance}像素，持续时间：500毫秒")
            
            # 执行滑动操作
            # swipe_element 参数说明：
            # - start_coords['x'], start_coords['y']: 滑动起始坐标
            # - end_coords['x'], end_coords['y']: 滑动结束坐标
            # - duration: 滑动持续时间（毫秒），影响滑动速度
            success = self.u2_manager.swipe_element(
                start_coords['x'], start_coords['y'],
                end_coords['x'], end_coords['y'],
                duration=500  # 滑动持续时间500毫秒，可根据需要调整（值越大滑动越慢）
            )
            
            if success:
                self.logger.info("向上滑动成功")
                # 滑动后等待时间，确保界面稳定
                time.sleep(self.wait_times['after_scroll'])
                return True
            else:
                self.logger.error("向上滑动失败")
                return False
                
        except Exception as e:
            self.logger.error(f"向上滑动异常：{str(e)}")
            return False
    
    def take_screenshot(self, name_prefix: str = "market") -> Optional[str]:
        """截取当前屏幕
        
        Args:
            name_prefix: 截图文件名前缀
            
        Returns:
            Optional[str]: 截图文件路径，失败返回None
        """
        try:
            self.logger.info(f"开始截图，前缀：{name_prefix}")
            
            # 使用UIAutomator2管理器截图
            screenshot_data = self.u2_manager.take_screenshot()
            if not screenshot_data:
                self.logger.error("截图失败：无法获取截图数据")
                return None
            
            # 生成文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            filename = f"{name_prefix}_{timestamp}.png"
            
            # 确保截图目录存在
            screenshot_dir = self.config_manager.get('screenshot', {}).get('save_path', 'data/screenshots/')
            import os
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # 保存截图
            file_path = os.path.join(screenshot_dir, filename)
            
            # 将字节数据保存为文件
            with open(file_path, 'wb') as f:
                f.write(screenshot_data)
            
            self.logger.info(f"截图成功，保存至：{file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"截图异常：{str(e)}")
            return None
    
    def scroll_up_800_pixels(self) -> bool:
        """向上滑动715像素
        
        滑动距离说明：
        - 起始位置：y = 900（屏幕中下部）
        - 结束位置：y = 185（屏幕中上部）
        - 滑动距离：900 - 185 = 715像素
        - 滑动持续时间：500毫秒
        
        Returns:
            bool: 操作是否成功
        """
        try:
            # 固定滑动坐标：从(360, 900)到(360, 185)，滑动715像素
            start_x, start_y = 360, 900
            end_x, end_y = 360, 185
            scroll_distance = abs(start_y - end_y)
            
            self.logger.info(f"向上滑动715像素，从({start_x}, {start_y})到({end_x}, {end_y})")
            self.logger.info(f"滑动距离：{scroll_distance}像素，持续时间：500毫秒")
            
            # 执行滑动操作
            success = self.u2_manager.swipe_element(
                start_x, start_y,
                end_x, end_y,
                duration=500  # 滑动持续时间500毫秒
            )
            
            if success:
                self.logger.info("向上滑动715像素成功")
                time.sleep(self.wait_times['after_scroll'])
                return True
            else:
                self.logger.error("向上滑动715像素失败")
                return False
                
        except Exception as e:
            self.logger.error(f"向上滑动715像素异常：{str(e)}")
            return False
    
    def execute_market_sequence(self) -> bool:
        """执行完整的市场操作序列
        
        Returns:
            bool: 整个序列是否执行成功
        """
        try:
            self.logger.info("开始执行市场操作序列")
            
            # 初始截图
            self.take_screenshot("market_initial")
            
            # 第一步：点击市场按钮
            if not self.click_market_button():
                self.logger.error("市场操作序列失败：点击市场按钮失败")
                return False
            
            # 点击市场按钮后截图
            self.take_screenshot("after_market_click")
            
            # 第二步：点击报价绿色按钮
            if not self.click_quote_button():
                self.logger.error("市场操作序列失败：点击报价绿色按钮失败")
                return False
            
            # 点击报价按钮后截图
            self.take_screenshot("after_quote_click")
            
            # 第三步：点击显示全部报价
            if not self.click_show_all_quotes():
                self.logger.error("市场操作序列失败：点击显示全部报价失败")
                return False
            
            # 点击显示全部报价后截图
            self.take_screenshot("after_show_all_quotes")
            
            # 第四步：向上滑动200像素
            if not self.scroll_up_at_quotes_position():
                self.logger.error("市场操作序列失败：向上滑动200像素失败")
                return False
            
            # 滑动后截图
            self.take_screenshot("after_scroll_200")
            
            # 第五步：截图
            self.logger.info("执行第五步：截图")
            self.take_screenshot("step5_screenshot")
            
            # 第六步：向上滚动800像素
            self.logger.info("执行第六步：向上滚动800像素")
            if not self.scroll_up_800_pixels():
                self.logger.error("市场操作序列失败：向上滚动800像素失败")
                return False
            
            # 滚动800像素后截图
            self.take_screenshot("after_scroll_800")
            
            self.logger.info("市场操作序列执行完成")
            return True
            
        except Exception as e:
            self.logger.error(f"执行市场操作序列异常：{str(e)}")
            return False
    
    def initialize(self) -> bool:
        """初始化模块
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.is_initialized = True
            self.start_time = time.time()
            self.logger.info("市场点击器初始化成功")
            return True
        except Exception as e:
            self.logger.error(f"市场点击器初始化失败：{str(e)}")
            return False
    
    def cleanup(self) -> bool:
        """清理模块资源
        
        Returns:
            bool: 清理是否成功
        """
        try:
            self.is_initialized = False
            self.logger.info("市场点击器资源清理完成")
            return True
        except Exception as e:
            self.logger.error(f"市场点击器资源清理失败：{str(e)}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取模块状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        status = super().get_status()
        status.update({
            'coordinates': self.coordinates,
            'wait_times': self.wait_times,
            'u2_manager_connected': self.u2_manager.is_connected if self.u2_manager else False
        })
        return status
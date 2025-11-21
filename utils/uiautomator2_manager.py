#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UIAutomator2管理器模块
提供Android设备UI自动化功能
"""

import time
import json
import traceback
from typing import Dict, Any, Optional, Tuple, List
from .interfaces import UIAutomator2Interface, BaseModule


class UIAutomator2Manager(BaseModule, UIAutomator2Interface):
    """UIAutomator2管理器实现类"""
    
    def __init__(self, config_manager, logger):
        """初始化UIAutomator2管理器
        
        Args:
            config_manager: 配置管理器实例
            logger: 日志记录器实例
        """
        super().__init__(config_manager, logger)
        self.device = None
        self.device_id = None
        self.device_info = None
        self.is_connected = False
        self._uiautomator2 = None
        
    def initialize(self) -> bool:
        """初始化模块
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 导入uiautomator2
            import uiautomator2 as u2
            self._uiautomator2 = u2
            
            # 加载配置
            self.config = self.config_manager.get('uiautomator2', {})
            
            # 连接设备
            device_id = self.config.get('device_id', None)
            if self.connect_device(device_id):
                self.is_initialized = True
                self.start_time = time.time()
                self.logger.info("UIAutomator2管理器初始化成功")
                return True
            else:
                self.logger.error("UIAutomator2管理器初始化失败：无法连接设备")
                return False
                
        except Exception as e:
            self.logger.error(f"UIAutomator2管理器初始化异常：{str(e)}")
            self.logger.debug(traceback.format_exc())
            return False
    
    def cleanup(self) -> bool:
        """清理模块资源
        
        Returns:
            bool: 清理是否成功
        """
        try:
            if self.device:
                self.disconnect_device()
            self.is_initialized = False
            self.logger.info("UIAutomator2管理器资源清理完成")
            return True
        except Exception as e:
            self.logger.error(f"UIAutomator2管理器资源清理异常：{str(e)}")
            return False
    
    def connect_device(self, device_id: Optional[str] = None) -> bool:
        """连接设备
        
        Args:
            device_id: 设备ID，None表示连接默认设备
            
        Returns:
            bool: 连接是否成功
        """
        try:
            if device_id:
                self.device = self._uiautomator2.connect(device_id)
            else:
                # 尝试连接USB设备，如果没有则尝试WiFi连接
                try:
                    self.device = self._uiautomator2.connect_usb()
                except:
                    self.device = self._uiautomator2.connect_wifi()
            
            if self.device:
                self.device_id = device_id or self.device.serial
                self.is_connected = True
                
                # 获取设备信息
                self.device_info = self.get_device_info()
                self.logger.info(f"成功连接设备：{self.device_id}")
                return True
            else:
                self.logger.error("无法连接设备")
                return False
                
        except Exception as e:
            self.logger.error(f"连接设备异常：{str(e)}")
            self.is_connected = False
            return False
    
    def disconnect_device(self) -> bool:
        """断开设备连接
        
        Returns:
            bool: 断开是否成功
        """
        try:
            if self.device:
                # UIAutomator2没有显式的断开连接方法
                # 只需要将引用置为None
                self.device = None
            self.is_connected = False
            self.device_id = None
            self.device_info = None
            self.logger.info("设备连接已断开")
            return True
        except Exception as e:
            self.logger.error(f"断开设备连接异常：{str(e)}")
            return False
    
    def get_device_info(self) -> Optional[Dict[str, Any]]:
        """获取设备信息
        
        Returns:
            Optional[Dict[str, Any]]: 设备信息
        """
        try:
            if not self.device:
                return None
                
            info = self.device.info
            return {
                'serial': info.get('serial'),
                'brand': info.get('brand'),
                'model': info.get('model'),
                'version': info.get('version'),
                'sdk': info.get('sdk'),
                'width': info.get('displayWidth'),
                'height': info.get('displayHeight'),
                'orientation': info.get('displayRotation'),
                'currentPackageName': info.get('currentPackageName')
            }
        except Exception as e:
            self.logger.error(f"获取设备信息异常：{str(e)}")
            return None
    
    def tap_element(self, x: int, y: int, duration: int = 100) -> bool:
        """点击元素
        
        Args:
            x: X坐标
            y: Y坐标
            duration: 点击持续时间（毫秒）
            
        Returns:
            bool: 操作是否成功
        """
        try:
            if not self.device:
                return False
                
            self.device.click(x, y)
            self.logger.debug(f"点击坐标：({x}, {y})")
            return True
        except Exception as e:
            self.logger.error(f"点击元素异常：{str(e)}")
            return False
    
    def swipe_element(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """滑动操作
        
        Args:
            x1: 起始X坐标
            y1: 起始Y坐标
            x2: 结束X坐标
            y2: 结束Y坐标
            duration: 滑动持续时间（毫秒）
            
        Returns:
            bool: 操作是否成功
        """
        try:
            if not self.device:
                return False
                
            self.device.swipe(x1, y1, x2, y2, duration/1000.0)  # 转换为秒
            self.logger.debug(f"滑动从({x1}, {y1})到({x2}, {y2})，持续时间：{duration}ms")
            return True
        except Exception as e:
            self.logger.error(f"滑动操作异常：{str(e)}")
            return False
    
    def find_element_by_text(self, text: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """通过文本查找元素
        
        Args:
            text: 查找的文本
            timeout: 超时时间（秒）
            
        Returns:
            Optional[Dict[str, Any]]: 元素信息
        """
        try:
            if not self.device:
                return None
                
            element = self.device(text=text).wait(timeout=timeout)
            if element and hasattr(element, 'exists') and element.exists:
                return self._element_to_dict(element)
            else:
                return None
        except Exception as e:
            self.logger.error(f"通过文本查找元素异常：{str(e)}")
            return None
    
    def find_element_by_id(self, resource_id: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """通过资源ID查找元素
        
        Args:
            resource_id: 资源ID
            timeout: 超时时间（秒）
            
        Returns:
            Optional[Dict[str, Any]]: 元素信息
        """
        try:
            if not self.device:
                return None
                
            element = self.device(resourceId=resource_id).wait(timeout=timeout)
            if element and hasattr(element, 'exists') and element.exists:
                return self._element_to_dict(element)
            else:
                return None
        except Exception as e:
            self.logger.error(f"通过资源ID查找元素异常：{str(e)}")
            return None
    
    def find_element_by_class(self, class_name: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """通过类名查找元素
        
        Args:
            class_name: 类名
            timeout: 超时时间（秒）
            
        Returns:
            Optional[Dict[str, Any]]: 元素信息
        """
        try:
            if not self.device:
                return None
                
            element = self.device(className=class_name).wait(timeout=timeout)
            if element and hasattr(element, 'exists') and element.exists:
                return self._element_to_dict(element)
            else:
                return None
        except Exception as e:
            self.logger.error(f"通过类名查找元素异常：{str(e)}")
            return None
    
    def get_element_bounds(self, element: Dict[str, Any]) -> Optional[Tuple[int, int, int, int]]:
        """获取元素边界
        
        Args:
            element: 元素信息
            
        Returns:
            Optional[Tuple[int, int, int, int]]: 边界坐标 (left, top, right, bottom)
        """
        try:
            bounds = element.get('bounds')
            if bounds:
                return (bounds['left'], bounds['top'], bounds['right'], bounds['bottom'])
            else:
                return None
        except Exception as e:
            self.logger.error(f"获取元素边界异常：{str(e)}")
            return None
    
    def get_element_center(self, element: Dict[str, Any]) -> Optional[Tuple[int, int]]:
        """获取元素中心点
        
        Args:
            element: 元素信息
            
        Returns:
            Optional[Tuple[int, int]]: 中心点坐标 (x, y)
        """
        try:
            bounds = self.get_element_bounds(element)
            if bounds:
                left, top, right, bottom = bounds
                center_x = (left + right) // 2
                center_y = (top + bottom) // 2
                return (center_x, center_y)
            else:
                return None
        except Exception as e:
            self.logger.error(f"获取元素中心点异常：{str(e)}")
            return None
    
    def click_element(self, element: Dict[str, Any]) -> bool:
        """点击元素
        
        Args:
            element: 元素信息
            
        Returns:
            bool: 操作是否成功
        """
        try:
            center = self.get_element_center(element)
            if center:
                x, y = center
                return self.tap_element(x, y)
            else:
                return False
        except Exception as e:
            self.logger.error(f"点击元素异常：{str(e)}")
            return False
    
    def long_click_element(self, element: Dict[str, Any], duration: int = 1000) -> bool:
        """长按元素
        
        Args:
            element: 元素信息
            duration: 长按持续时间（毫秒）
            
        Returns:
            bool: 操作是否成功
        """
        try:
            center = self.get_element_center(element)
            if center:
                x, y = center
                self.device.long_click(x, y, duration/1000.0)  # 转换为秒
                self.logger.debug(f"长按坐标：({x}, {y})，持续时间：{duration}ms")
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"长按元素异常：{str(e)}")
            return False
    
    def input_text(self, element: Dict[str, Any], text: str) -> bool:
        """输入文本
        
        Args:
            element: 元素信息
            text: 输入的文本
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 先点击元素获取焦点
            if not self.click_element(element):
                return False
                
            # 输入文本
            self.device.send_keys(text)
            self.logger.debug(f"输入文本：{text}")
            return True
        except Exception as e:
            self.logger.error(f"输入文本异常：{str(e)}")
            return False
    
    def clear_text(self, element: Dict[str, Any]) -> bool:
        """清空文本
        
        Args:
            element: 元素信息
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 先点击元素获取焦点
            if not self.click_element(element):
                return False
                
            # 全选并删除
            self.device.clear_text()
            self.logger.debug("清空文本")
            return True
        except Exception as e:
            self.logger.error(f"清空文本异常：{str(e)}")
            return False
    
    def scroll_to_element(self, element: Dict[str, Any]) -> bool:
        """滚动到元素
        
        Args:
            element: 目标元素
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 获取元素中心点
            center = self.get_element_center(element)
            if not center:
                return False
                
            x, y = center
            
            # 向上或向下滚动直到元素可见
            screen_height = self.device_info.get('height', 1920)
            scroll_steps = 5
            
            for _ in range(scroll_steps):
                # 检查元素是否可见
                if 0 <= y <= screen_height:
                    return True
                    
                # 向上滚动
                self.device.swipe(x, screen_height * 0.8, x, screen_height * 0.2, 0.5)
                time.sleep(0.5)
                
            return False
        except Exception as e:
            self.logger.error(f"滚动到元素异常：{str(e)}")
            return False
    
    def get_current_app(self) -> Optional[Dict[str, Any]]:
        """获取当前应用信息
        
        Returns:
            Optional[Dict[str, Any]]: 应用信息
        """
        try:
            if not self.device:
                return None
                
            app_info = self.device.app_current()
            return {
                'package': app_info.get('package'),
                'activity': app_info.get('activity'),
                'pid': app_info.get('pid')
            }
        except Exception as e:
            self.logger.error(f"获取当前应用信息异常：{str(e)}")
            return None
    
    def start_app(self, package_name: str, activity: Optional[str] = None) -> bool:
        """启动应用
        
        Args:
            package_name: 包名
            activity: Activity名称
            
        Returns:
            bool: 启动是否成功
        """
        try:
            if not self.device:
                return False
                
            if activity:
                self.device.app_start(package_name, activity)
            else:
                self.device.app_start(package_name)
                
            self.logger.debug(f"启动应用：{package_name}")
            return True
        except Exception as e:
            self.logger.error(f"启动应用异常：{str(e)}")
            return False
    
    def stop_app(self, package_name: str) -> bool:
        """停止应用
        
        Args:
            package_name: 包名
            
        Returns:
            bool: 停止是否成功
        """
        try:
            if not self.device:
                return False
                
            self.device.app_stop(package_name)
            self.logger.debug(f"停止应用：{package_name}")
            return True
        except Exception as e:
            self.logger.error(f"停止应用异常：{str(e)}")
            return False
    
    def dump_hierarchy(self) -> Optional[str]:
        """获取界面层次结构
        
        Returns:
            Optional[str]: XML格式的界面层次结构
        """
        try:
            if not self.device:
                return None
                
            xml_content = self.device.dump_hierarchy()
            return xml_content
        except Exception as e:
            self.logger.error(f"获取界面层次结构异常：{str(e)}")
            return None
    
    def take_screenshot(self) -> Optional[bytes]:
        """截取屏幕
        
        Returns:
            Optional[bytes]: 截图数据
        """
        try:
            if not self.device:
                return None
                
            screenshot = self.device.screenshot()
            if screenshot:
                import io
                img_bytes = io.BytesIO()
                screenshot.save(img_bytes, format='PNG')
                return img_bytes.getvalue()
            else:
                return None
        except Exception as e:
            self.logger.error(f"截取屏幕异常：{str(e)}")
            return None
    
    def _element_to_dict(self, element) -> Dict[str, Any]:
        """将UIAutomator2元素转换为字典
        
        Args:
            element: UIAutomator2元素对象
            
        Returns:
            Dict[str, Any]: 元素信息字典
        """
        try:
            info = element.info
            return {
                'text': info.get('text', ''),
                'resource_id': info.get('resourceId', ''),
                'class_name': info.get('className', ''),
                'package': info.get('package', ''),
                'content_desc': info.get('contentDesc', ''),
                'enabled': info.get('enabled', False),
                'focusable': info.get('focusable', False),
                'focused': info.get('focused', False),
                'scrollable': info.get('scrollable', False),
                'long_clickable': info.get('longClickable', False),
                'password': info.get('password', False),
                'selected': info.get('selected', False),
                'bounds': info.get('bounds', {}),
                'checkable': info.get('checkable', False),
                'checked': info.get('checked', False),
                'clickable': info.get('clickable', False)
            }
        except Exception as e:
            self.logger.error(f"转换元素信息异常：{str(e)}")
            return {}
    
    def get_status(self) -> Dict[str, Any]:
        """获取模块状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        status = super().get_status()
        status.update({
            'connected': self.is_connected,
            'device_id': self.device_id,
            'device_info': self.device_info
        })
        return status
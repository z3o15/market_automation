#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块间基础接口和抽象类
定义各模块间的标准接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
import time


class BaseModule(ABC):
    """基础模块抽象类"""
    
    def __init__(self, config_manager, logger):
        """初始化基础模块
        
        Args:
            config_manager: 配置管理器实例
            logger: 日志记录器实例
        """
        self.config_manager = config_manager
        self.logger = logger
        self.config = {}
        self.is_initialized = False
        self.start_time = 0
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化模块
        
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """清理模块资源
        
        Returns:
            bool: 清理是否成功
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """获取模块状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        return {
            "initialized": self.is_initialized,
            "uptime": time.time() - self.start_time if self.start_time > 0 else 0
        }


class ScreenshotInterface(ABC):
    """截图管理接口"""
    
    @abstractmethod
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[bytes]:
        """截取屏幕
        
        Args:
            region: 截图区域 (x, y, width, height)，None表示全屏
            
        Returns:
            Optional[bytes]: 截图数据
        """
        pass
    
    @abstractmethod
    def save_screenshot(self, image_data: bytes, path: str) -> bool:
        """保存截图
        
        Args:
            image_data: 图像数据
            path: 保存路径
            
        Returns:
            bool: 保存是否成功
        """
        pass
    
    @abstractmethod
    def get_latest_screenshot(self) -> Optional[bytes]:
        """获取最新截图
        
        Returns:
            Optional[bytes]: 截图数据
        """
        pass


class ADBInterface(ABC):
    """ADB控制接口"""
    
    @abstractmethod
    def execute_command(self, command: str, timeout: int = 30) -> Optional[str]:
        """执行ADB命令
        
        Args:
            command: ADB命令
            timeout: 超时时间（秒）
            
        Returns:
            Optional[str]: 命令输出
        """
        pass
    
    @abstractmethod
    def tap(self, x: int, y: int, duration: int = 100) -> bool:
        """点击屏幕
        
        Args:
            x: X坐标
            y: Y坐标
            duration: 点击持续时间（毫秒）
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    @abstractmethod
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
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
        pass


class ImageRecognitionInterface(ABC):
    """图像识别接口"""
    
    @abstractmethod
    def recognize_text(self, image_data: bytes, language: str = 'chi_sim') -> Optional[Dict[str, Any]]:
        """OCR文字识别
        
        Args:
            image_data: 图像数据
            language: 识别语言
            
        Returns:
            Optional[Dict[str, Any]]: 识别结果
        """
        pass
    
    @abstractmethod
    def match_template(self, image_data: bytes, template_data: bytes, threshold: float = 0.8) -> Optional[Dict[str, Any]]:
        """模板匹配
        
        Args:
            image_data: 源图像数据
            template_data: 模板图像数据
            threshold: 匹配阈值
            
        Returns:
            Optional[Dict[str, Any]]: 匹配结果
        """
        pass
    
    @abstractmethod
    def locate_element(self, image_data: bytes, element_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """定位界面元素
        
        Args:
            image_data: 图像数据
            element_config: 元素配置
            
        Returns:
            Optional[Dict[str, Any]]: 定位结果
        """
        pass


class DataProcessingInterface(ABC):
    """数据处理接口"""
    
    @abstractmethod
    def extract_equipment_data(self, image_data: bytes, recognition_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """提取装备数据
        
        Args:
            image_data: 图像数据
            recognition_result: 识别结果
            
        Returns:
            Optional[Dict[str, Any]]: 装备数据
        """
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """验证数据
        
        Args:
            data: 待验证数据
            
        Returns:
            bool: 验证是否通过
        """
        pass
    
    @abstractmethod
    def save_data(self, data: Dict[str, Any]) -> bool:
        """保存数据
        
        Args:
            data: 待保存数据
            
        Returns:
            bool: 保存是否成功
        """
        pass


class DatabaseInterface(ABC):
    """数据库接口"""
    
    @abstractmethod
    def connect(self) -> bool:
        """连接数据库
        
        Returns:
            bool: 连接是否成功
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """断开数据库连接
        
        Returns:
            bool: 断开是否成功
        """
        pass
    
    @abstractmethod
    def query(self, sql: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """执行查询
        
        Args:
            sql: SQL语句
            params: 参数
            
        Returns:
            List[Dict[str, Any]]: 查询结果
        """
        pass
    
    @abstractmethod
    def execute(self, sql: str, params: Tuple = ()) -> bool:
        """执行SQL语句
        
        Args:
            sql: SQL语句
            params: 参数
            
        Returns:
            bool: 执行是否成功
        """
        pass


class AutomationInterface(ABC):
    """自动化控制接口"""
    
    @abstractmethod
    def start_automation(self) -> bool:
        """启动自动化流程
        
        Returns:
            bool: 启动是否成功
        """
        pass
    
    @abstractmethod
    def stop_automation(self) -> bool:
        """停止自动化流程
        
        Returns:
            bool: 停止是否成功
        """
        pass
    
    @abstractmethod
    def pause_automation(self) -> bool:
        """暂停自动化流程
        
        Returns:
            bool: 暂停是否成功
        """
        pass
    
    @abstractmethod
    def resume_automation(self) -> bool:
        """恢复自动化流程
        
        Returns:
            bool: 恢复是否成功
        """
        pass
    
    @abstractmethod
    def get_automation_status(self) -> Dict[str, Any]:
        """获取自动化状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        pass


class UIAutomator2Interface(ABC):
    """UIAutomator2控制接口"""
    
    @abstractmethod
    def connect_device(self, device_id: Optional[str] = None) -> bool:
        """连接设备
        
        Args:
            device_id: 设备ID，None表示连接默认设备
            
        Returns:
            bool: 连接是否成功
        """
        pass
    
    @abstractmethod
    def disconnect_device(self) -> bool:
        """断开设备连接
        
        Returns:
            bool: 断开是否成功
        """
        pass
    
    @abstractmethod
    def get_device_info(self) -> Optional[Dict[str, Any]]:
        """获取设备信息
        
        Returns:
            Optional[Dict[str, Any]]: 设备信息
        """
        pass
    
    @abstractmethod
    def tap_element(self, x: int, y: int, duration: int = 100) -> bool:
        """点击元素
        
        Args:
            x: X坐标
            y: Y坐标
            duration: 点击持续时间（毫秒）
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def find_element_by_text(self, text: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """通过文本查找元素
        
        Args:
            text: 查找的文本
            timeout: 超时时间（秒）
            
        Returns:
            Optional[Dict[str, Any]]: 元素信息
        """
        pass
    
    @abstractmethod
    def find_element_by_id(self, resource_id: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """通过资源ID查找元素
        
        Args:
            resource_id: 资源ID
            timeout: 超时时间（秒）
            
        Returns:
            Optional[Dict[str, Any]]: 元素信息
        """
        pass
    
    @abstractmethod
    def find_element_by_class(self, class_name: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """通过类名查找元素
        
        Args:
            class_name: 类名
            timeout: 超时时间（秒）
            
        Returns:
            Optional[Dict[str, Any]]: 元素信息
        """
        pass
    
    @abstractmethod
    def get_element_bounds(self, element: Dict[str, Any]) -> Optional[Tuple[int, int, int, int]]:
        """获取元素边界
        
        Args:
            element: 元素信息
            
        Returns:
            Optional[Tuple[int, int, int, int]]: 边界坐标 (left, top, right, bottom)
        """
        pass
    
    @abstractmethod
    def get_element_center(self, element: Dict[str, Any]) -> Optional[Tuple[int, int]]:
        """获取元素中心点
        
        Args:
            element: 元素信息
            
        Returns:
            Optional[Tuple[int, int]]: 中心点坐标 (x, y)
        """
        pass
    
    @abstractmethod
    def click_element(self, element: Dict[str, Any]) -> bool:
        """点击元素
        
        Args:
            element: 元素信息
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    @abstractmethod
    def long_click_element(self, element: Dict[str, Any], duration: int = 1000) -> bool:
        """长按元素
        
        Args:
            element: 元素信息
            duration: 长按持续时间（毫秒）
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    @abstractmethod
    def input_text(self, element: Dict[str, Any], text: str) -> bool:
        """输入文本
        
        Args:
            element: 元素信息
            text: 输入的文本
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    @abstractmethod
    def clear_text(self, element: Dict[str, Any]) -> bool:
        """清空文本
        
        Args:
            element: 元素信息
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    @abstractmethod
    def scroll_to_element(self, element: Dict[str, Any]) -> bool:
        """滚动到元素
        
        Args:
            element: 目标元素
            
        Returns:
            bool: 操作是否成功
        """
        pass
    
    @abstractmethod
    def get_current_app(self) -> Optional[Dict[str, Any]]:
        """获取当前应用信息
        
        Returns:
            Optional[Dict[str, Any]]: 应用信息
        """
        pass
    
    @abstractmethod
    def start_app(self, package_name: str, activity: Optional[str] = None) -> bool:
        """启动应用
        
        Args:
            package_name: 包名
            activity: Activity名称
            
        Returns:
            bool: 启动是否成功
        """
        pass
    
    @abstractmethod
    def stop_app(self, package_name: str) -> bool:
        """停止应用
        
        Args:
            package_name: 包名
            
        Returns:
            bool: 停止是否成功
        """
        pass
    
    @abstractmethod
    def dump_hierarchy(self) -> Optional[str]:
        """获取界面层次结构
        
        Returns:
            Optional[str]: XML格式的界面层次结构
        """
        pass
    
    @abstractmethod
    def take_screenshot(self) -> Optional[bytes]:
        """截取屏幕
        
        Returns:
            Optional[bytes]: 截图数据
        """
        pass


class CoordinateAdapterInterface(ABC):
    """坐标适配器接口"""
    
    @abstractmethod
    def convert_coordinates(self, x: int, y: int, source_system: str, target_system: str) -> Tuple[int, int]:
        """坐标转换
        
        Args:
            x: 源X坐标
            y: 源Y坐标
            source_system: 源坐标系统
            target_system: 目标坐标系统
            
        Returns:
            Tuple[int, int]: 转换后的坐标 (x, y)
        """
        pass
    
    @abstractmethod
    def normalize_coordinates(self, x: int, y: int, screen_width: int, screen_height: int) -> Tuple[float, float]:
        """归一化坐标
        
        Args:
            x: 原始X坐标
            y: 原始Y坐标
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            
        Returns:
            Tuple[float, float]: 归一化坐标 (0.0-1.0, 0.0-1.0)
        """
        pass
    
    @abstractmethod
    def denormalize_coordinates(self, norm_x: float, norm_y: float, screen_width: int, screen_height: int) -> Tuple[int, int]:
        """反归一化坐标
        
        Args:
            norm_x: 归一化X坐标
            norm_y: 归一化Y坐标
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            
        Returns:
            Tuple[int, int]: 实际坐标 (x, y)
        """
        pass
    
    @abstractmethod
    def scale_coordinates(self, x: int, y: int, scale_factor: float) -> Tuple[int, int]:
        """缩放坐标
        
        Args:
            x: 原始X坐标
            y: 原始Y坐标
            scale_factor: 缩放因子
            
        Returns:
            Tuple[int, int]: 缩放后的坐标 (x, y)
        """
        pass
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件存储管理器
简化版本，仅用于基本的文件存储和管理功能
主要功能：
- 截图保存
- 操作日志保存
- 文件清理
"""

import os
import json
import time
import shutil
import gzip
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import threading
from pathlib import Path

from database.models import OperationLog, Statistics


class FileStorageManager:
    """文件存储管理器
    
    提供基本的文件存储和管理功能，包括：
    - 截图保存和管理
    - 操作日志保存
    - 文件清理功能
    """
    
    def __init__(self, config_manager, logger):
        """初始化文件存储管理器
        
        Args:
            config_manager: 配置管理器实例
            logger: 日志记录器实例
        """
        self.config_manager = config_manager
        self.logger = logger
        self.config = config_manager.get('database', {})
        self.file_storage_config = self.config.get('fileStorage', {})
        self.retention_config = self.config.get('retention', {})
        
        # 数据路径
        self.data_path = self.config.get('dataPath', './data')
        self.subdirectories = self.config.get('subdirectories', {})
        
        # 线程锁
        self.lock = threading.Lock()
        
        # 初始化目录
        self._initialize_directories()
    
    def _initialize_directories(self):
        """初始化目录结构"""
        try:
            # 创建主数据目录
            os.makedirs(self.data_path, exist_ok=True)
            
            # 创建子目录
            for subdir_name, subdir_path in self.subdirectories.items():
                full_path = os.path.join(self.data_path, subdir_path)
                os.makedirs(full_path, exist_ok=True)
            
            self.logger.info("文件存储目录初始化完成")
        except Exception as e:
            self.logger.error(f"初始化文件存储目录失败: {e}")
    
    
    def save_screenshot(self, image_data: bytes, filename: str = None) -> str:
        """保存截图
        
        Args:
            image_data: 图像数据
            filename: 文件名，如果为None则自动生成
            
        Returns:
            str: 保存的文件路径
        """
        try:
            with self.lock:
                # 生成文件名
                if not filename:
                    timestamp = int(time.time() * 1000)  # 使用毫秒时间戳避免重复
                    filename = f"screenshot_{timestamp}.png"
                
                screenshot_dir = os.path.join(self.data_path, self.subdirectories.get('screenshots', 'screenshots'))
                
                # 确保目录存在
                os.makedirs(screenshot_dir, exist_ok=True)
                
                filepath = os.path.join(screenshot_dir, filename)
                
                # 保存图像
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                self.logger.debug(f"截图保存成功: {filepath}")
                return filepath
        except Exception as e:
            self.logger.error(f"保存截图时发生错误: {e}")
            return ""
    
    
    def save_operation_log(self, operation_log: OperationLog) -> bool:
        """保存操作日志
        
        Args:
            operation_log: 操作日志对象
            
        Returns:
            bool: 保存是否成功
        """
        try:
            with self.lock:
                # 生成文件名
                timestamp = int(operation_log.timestamp)
                date_str = datetime.fromtimestamp(timestamp).strftime('%Y%m%d')
                filename = f"operation_{date_str}.log"
                filepath = os.path.join(self.data_path, self.subdirectories.get('logs', 'logs'), filename)
                
                # 追加日志到文件
                log_entry = f"[{operation_log.formatted_time}] {operation_log.operation_type}: {operation_log.result}\n"
                if operation_log.error_message:
                    log_entry += f"Error: {operation_log.error_message}\n"
                
                with open(filepath, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                
                self.logger.debug(f"操作日志保存成功: {filepath}")
                return True
        except Exception as e:
            self.logger.error(f"保存操作日志时发生错误: {e}")
            return False
    
    
    def get_screenshots(self, limit: int = 100) -> List[str]:
        """获取截图列表
        
        Args:
            limit: 限制数量
            
        Returns:
            List[str]: 截图路径列表
        """
        try:
            screenshot_dir = os.path.join(self.data_path, self.subdirectories.get('screenshots', 'screenshots'))
            screenshots = []
            
            # 检查目录是否存在
            if not os.path.exists(screenshot_dir):
                return screenshots
            
            # 遍历截图文件
            for filename in os.listdir(screenshot_dir):
                if filename.endswith('.png') or filename.endswith('.jpg'):
                    filepath = os.path.join(screenshot_dir, filename)
                    screenshots.append(filepath)
            
            # 按修改时间排序（最新的在前）
            screenshots.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            return screenshots[:limit]
        except Exception as e:
            self.logger.error(f"获取截图列表时发生错误: {e}")
            return []
    
    def _matches_filters(self, data: Dict[str, Any], filters: Dict[str, Any] = None) -> bool:
        """检查数据是否匹配过滤条件"""
        if not filters:
            return True
        
        try:
            # 名称过滤
            if 'name' in filters and filters['name']:
                if filters['name'].lower() not in data.get('name', '').lower():
                    return False
            
            # 价格范围过滤
            if 'price_min' in filters and filters['price_min'] is not None:
                if data.get('price', 0) < filters['price_min']:
                    return False
            
            if 'price_max' in filters and filters['price_max'] is not None:
                if data.get('price', 0) > filters['price_max']:
                    return False
            
            # 品质过滤
            if 'quality' in filters and filters['quality']:
                if data.get('quality', '') != filters['quality']:
                    return False
            
            # 类型过滤
            if 'type' in filters and filters['type']:
                if data.get('type', '') != filters['type']:
                    return False
            
            # 时间范围过滤
            if 'start_time' in filters and filters['start_time']:
                if data.get('timestamp', 0) < filters['start_time']:
                    return False
            
            if 'end_time' in filters and filters['end_time']:
                if data.get('timestamp', 0) > filters['end_time']:
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"检查过滤条件时发生错误: {e}")
            return True
    
    def cleanup_old_files(self) -> bool:
        """清理旧文件"""
        try:
            current_time = time.time()
            cleaned_files = 0
            
            # 清理截图
            screenshot_retention = self.retention_config.get('screenshots', 7)
            cleaned_files += self._cleanup_directory(
                os.path.join(self.data_path, self.subdirectories.get('screenshots', 'screenshots')),
                screenshot_retention * 24 * 3600
            )
            
            # 分析结果功能已移除，不再清理相关目录
            
            # 清理日志
            logs_retention = self.retention_config.get('logs', 30)
            cleaned_files += self._cleanup_directory(
                os.path.join(self.data_path, self.subdirectories.get('logs', 'logs')),
                logs_retention * 24 * 3600
            )
            
            # 清理缓存
            cache_retention = self.retention_config.get('cache', 1)
            cleaned_files += self._cleanup_directory(
                os.path.join(self.data_path, self.subdirectories.get('cache', 'cache')),
                cache_retention * 24 * 3600
            )
            
            self.logger.info(f"清理旧文件完成，共清理 {cleaned_files} 个文件")
            return True
        except Exception as e:
            self.logger.error(f"清理旧文件时发生错误: {e}")
            return False
    
    def _cleanup_directory(self, directory: str, max_age: int) -> int:
        """清理指定目录中的旧文件
        
        Args:
            directory: 目录路径
            max_age: 最大年龄（秒）
            
        Returns:
            int: 清理的文件数量
        """
        try:
            if not os.path.exists(directory):
                return 0
            
            current_time = time.time()
            cleaned_count = 0
            
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getmtime(filepath)
                    
                    if file_age > max_age:
                        try:
                            os.remove(filepath)
                            cleaned_count += 1
                            self.logger.debug(f"删除旧文件: {filepath}")
                        except Exception as e:
                            self.logger.warning(f"删除文件失败: {filepath}, 错误: {e}")
            
            return cleaned_count
        except Exception as e:
            self.logger.error(f"清理目录时发生错误: {directory}, 错误: {e}")
            return 0
    
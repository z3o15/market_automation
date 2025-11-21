#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志记录器
负责记录和管理日志信息
"""

import os
import sys
import logging
import logging.handlers
from typing import Optional


class Logger:
    """日志记录器类"""
    
    def __init__(self, 
                 level: str = "INFO",
                 log_file: Optional[str] = None,
                 max_file_size: str = "10MB",
                 max_files: int = 5,
                 console_output: bool = True):
        """初始化日志记录器
        
        Args:
            level: 日志级别
            log_file: 日志文件路径
            max_file_size: 最大文件大小
            max_files: 最大文件数量
            console_output: 是否输出到控制台
        """
        self.logger = logging.getLogger("MarketAutomation")
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # 清除现有处理器
        self.logger.handlers.clear()
        
        # 设置日志格式
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] [%(threadName)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 添加控制台处理器
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # 添加文件处理器
        if log_file:
            # 解析文件大小
            size_bytes = self._parse_size(max_file_size)
            
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            # 创建轮转文件处理器
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=size_bytes,
                backupCount=max_files,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def _parse_size(self, size_str: str) -> int:
        """解析文件大小字符串
        
        Args:
            size_str: 大小字符串，如 "10MB"
            
        Returns:
            int: 字节数
        """
        size_str = size_str.upper().strip()
        
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def debug(self, message: str):
        """记录调试信息
        
        Args:
            message: 日志消息
        """
        self.logger.debug(message)
    
    def info(self, message: str):
        """记录一般信息
        
        Args:
            message: 日志消息
        """
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录警告信息
        
        Args:
            message: 日志消息
        """
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录错误信息
        
        Args:
            message: 日志消息
        """
        self.logger.error(message)
    
    def critical(self, message: str):
        """记录严重错误信息
        
        Args:
            message: 日志消息
        """
        self.logger.critical(message)
    
    def exception(self, message: str):
        """记录异常信息
        
        Args:
            message: 日志消息
        """
        self.logger.exception(message)
    
    def set_level(self, level: str):
        """设置日志级别
        
        Args:
            level: 日志级别
        """
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    def get_level(self) -> str:
        """获取当前日志级别
        
        Returns:
            str: 日志级别
        """
        return logging.getLevelName(self.logger.level)
    
    def add_file_handler(self, log_file: str, max_file_size: str = "10MB", max_files: int = 5):
        """添加文件处理器
        
        Args:
            log_file: 日志文件路径
            max_file_size: 最大文件大小
            max_files: 最大文件数量
        """
        # 解析文件大小
        size_bytes = self._parse_size(max_file_size)
        
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] [%(threadName)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 创建轮转文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=size_bytes,
            backupCount=max_files,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def remove_file_handler(self, log_file: str):
        """移除文件处理器
        
        Args:
            log_file: 日志文件路径
        """
        for handler in self.logger.handlers[:]:
            if isinstance(handler, logging.handlers.RotatingFileHandler) and handler.baseFilename == os.path.abspath(log_file):
                handler.close()
                self.logger.removeHandler(handler)
    
    def clear_handlers(self):
        """清除所有处理器"""
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)
    
    def log_function_call(self, func_name: str, args: tuple = (), kwargs: dict = None):
        """记录函数调用
        
        Args:
            func_name: 函数名
            args: 位置参数
            kwargs: 关键字参数
        """
        kwargs = kwargs or {}
        args_str = ", ".join([str(arg) for arg in args])
        kwargs_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        
        params = []
        if args_str:
            params.append(args_str)
        if kwargs_str:
            params.append(kwargs_str)
        
        params_str = ", ".join(params)
        self.debug(f"调用函数: {func_name}({params_str})")
    
    def log_performance(self, operation: str, duration: float, details: str = ""):
        """记录性能信息
        
        Args:
            operation: 操作名称
            duration: 持续时间（秒）
            details: 详细信息
        """
        message = f"性能统计: {operation} 耗时 {duration:.3f}秒"
        if details:
            message += f" - {details}"
        self.info(message)
    
    def log_network_request(self, method: str, url: str, status_code: int = None, response_time: float = None):
        """记录网络请求
        
        Args:
            method: HTTP方法
            url: 请求URL
            status_code: 响应状态码
            response_time: 响应时间（秒）
        """
        message = f"网络请求: {method} {url}"
        if status_code is not None:
            message += f" - 状态码: {status_code}"
        if response_time is not None:
            message += f" - 响应时间: {response_time:.3f}秒"
        
        if status_code and 200 <= status_code < 300:
            self.info(message)
        else:
            self.warning(message)
    
    def log_error_with_traceback(self, message: str, exception: Exception):
        """记录错误信息和堆栈跟踪
        
        Args:
            message: 错误消息
            exception: 异常对象
        """
        self.error(f"{message}: {str(exception)}")
        self.debug(f"异常堆栈: {exception.__class__.__name__}: {str(exception)}")
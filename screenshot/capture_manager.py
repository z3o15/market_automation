#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图捕获管理器
负责截图任务调度、批量截图处理、截图存储管理和截图历史记录等功能
"""

import os
import time
import json
import threading
import asyncio
from typing import Dict, Any, Optional, List, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import queue

from utils.interfaces import BaseModule
from utils.logger import Logger
from utils.config_manager import ConfigManager
from utils.device_manager import DeviceManager
from screenshot.screenshot_manager import ScreenshotManager
from screenshot.image_processor import ImageProcessor


@dataclass
class CaptureTask:
    """截图任务数据类"""
    task_id: str
    region: Optional[Tuple[int, int, int, int]]
    interval: float
    count: int
    current_count: int = 0
    created_time: float = 0
    next_capture_time: float = 0
    callback: Optional[Callable] = None
    auto_save: bool = True
    save_path: Optional[str] = None
    preprocess: bool = True
    compress: bool = True


@dataclass
class CaptureRecord:
    """截图记录数据类"""
    record_id: str
    task_id: str
    timestamp: float
    file_path: Optional[str]
    file_size: int
    width: int
    height: int
    format: str
    region: Optional[Tuple[int, int, int, int]]
    processing_time: float
    success: bool
    error_message: Optional[str] = None


class CaptureManager(BaseModule):
    """截图捕获管理器类"""
    
    def __init__(self, config_manager: ConfigManager, logger: Logger, 
                 device_manager: DeviceManager, screenshot_manager: ScreenshotManager,
                 image_processor: ImageProcessor):
        """初始化截图捕获管理器
        
        Args:
            config_manager: 配置管理器实例
            logger: 日志记录器实例
            device_manager: 设备管理器实例
            screenshot_manager: 截图管理器实例
            image_processor: 图片处理器实例
        """
        super().__init__(config_manager, logger)
        
        self.device_manager = device_manager
        self.screenshot_manager = screenshot_manager
        self.image_processor = image_processor
        
        # 配置
        self.data_config = self.config_manager.get("data", {})
        self.retention_config = self.data_config.get("retention", {})
        
        # 存储路径
        self.screenshot_dir = "data/screenshots"
        self.history_file = os.path.join(self.screenshot_dir, "capture_history.json")
        
        # 任务管理
        self.capture_tasks = {}
        self.task_queue = queue.Queue()
        self.task_lock = threading.RLock()
        
        # 历史记录
        self.capture_history = []
        self.history_lock = threading.RLock()
        
        # 调度器
        self.scheduler_thread = None
        self.worker_thread = None
        self.is_running = False
        
        # 性能统计
        self.total_captures = 0
        self.successful_captures = 0
        self.failed_captures = 0
        self.total_capture_time = 0
        
        # 创建目录
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def initialize(self) -> bool:
        """初始化截图捕获管理器
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.logger.info("初始化截图捕获管理器")
            
            # 检查依赖模块
            if not self._check_dependencies():
                return False
            
            # 加载历史记录
            self._load_history()
            
            # 清理过期记录
            self._cleanup_expired_records()
            
            # 启动调度器
            self._start_scheduler()
            
            self.is_initialized = True
            self.start_time = time.time()
            
            self.logger.info("截图捕获管理器初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"截图捕获管理器初始化失败: {e}")
            return False
    
    def cleanup(self) -> bool:
        """清理截图捕获管理器资源
        
        Returns:
            bool: 清理是否成功
        """
        try:
            self.logger.info("清理截图捕获管理器资源")
            
            # 停止调度器
            self._stop_scheduler()
            
            # 保存历史记录
            self._save_history()
            
            # 清理任务
            with self.task_lock:
                self.capture_tasks.clear()
            
            self.is_initialized = False
            self.logger.info("截图捕获管理器资源清理完成")
            return True
            
        except Exception as e:
            self.logger.error(f"截图捕获管理器资源清理失败: {e}")
            return False
    
    def schedule_capture(self, region: Optional[Tuple[int, int, int, int]] = None,
                         interval: float = 1.0, count: int = 1,
                         callback: Optional[Callable] = None,
                         auto_save: bool = True, save_path: Optional[str] = None,
                         preprocess: bool = True, compress: bool = True) -> str:
        """调度截图任务
        
        Args:
            region: 截图区域
            interval: 截图间隔（秒）
            count: 截图次数
            callback: 回调函数
            auto_save: 是否自动保存
            save_path: 保存路径
            preprocess: 是否预处理
            compress: 是否压缩
            
        Returns:
            str: 任务ID
        """
        try:
            # 生成任务ID
            task_id = f"capture_{int(time.time() * 1000)}_{self.total_captures}"
            
            # 创建任务
            task = CaptureTask(
                task_id=task_id,
                region=region,
                interval=interval,
                count=count,
                created_time=time.time(),
                next_capture_time=time.time(),
                callback=callback,
                auto_save=auto_save,
                save_path=save_path,
                preprocess=preprocess,
                compress=compress
            )
            
            # 添加到任务列表
            with self.task_lock:
                self.capture_tasks[task_id] = task
            
            self.logger.info(f"调度截图任务: {task_id}, 区域: {region}, 间隔: {interval}秒, 次数: {count}")
            return task_id
            
        except Exception as e:
            self.logger.error(f"调度截图任务失败: {e}")
            return ""
    
    def cancel_task(self, task_id: str) -> bool:
        """取消截图任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 取消是否成功
        """
        try:
            with self.task_lock:
                if task_id in self.capture_tasks:
                    del self.capture_tasks[task_id]
                    self.logger.info(f"取消截图任务: {task_id}")
                    return True
                else:
                    self.logger.warning(f"任务不存在: {task_id}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"取消任务失败: {e}")
            return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[Dict[str, Any]]: 任务状态
        """
        try:
            with self.task_lock:
                if task_id in self.capture_tasks:
                    task = self.capture_tasks[task_id]
                    return {
                        "task_id": task.task_id,
                        "region": task.region,
                        "interval": task.interval,
                        "count": task.count,
                        "current_count": task.current_count,
                        "created_time": task.created_time,
                        "next_capture_time": task.next_capture_time,
                        "progress": task.current_count / task.count if task.count > 0 else 0,
                        "is_completed": task.current_count >= task.count
                    }
                else:
                    return None
                    
        except Exception as e:
            self.logger.error(f"获取任务状态失败: {e}")
            return None
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """获取所有任务状态
        
        Returns:
            List[Dict[str, Any]]: 任务状态列表
        """
        try:
            with self.task_lock:
                return [self.get_task_status(task_id) for task_id in self.capture_tasks]
                
        except Exception as e:
            self.logger.error(f"获取所有任务失败: {e}")
            return []
    
    def batch_capture(self, regions: List[Tuple[int, int, int, int]], 
                     save_dir: Optional[str] = None) -> List[str]:
        """批量截图
        
        Args:
            regions: 截图区域列表
            save_dir: 保存目录
            
        Returns:
            List[str]: 截图文件路径列表
        """
        try:
            self.logger.info(f"开始批量截图，区域数量: {len(regions)}")
            
            if save_dir is None:
                save_dir = os.path.join(self.screenshot_dir, f"batch_{int(time.time())}")
            
            os.makedirs(save_dir, exist_ok=True)
            
            file_paths = []
            
            for i, region in enumerate(regions):
                # 截图
                screenshot_data = self.screenshot_manager.capture_screen(region)
                if not screenshot_data:
                    self.logger.error(f"批量截图失败，区域: {region}")
                    continue
                
                # 处理图片
                processed_data = self._process_screenshot(screenshot_data, True, True)
                if not processed_data:
                    self.logger.error(f"图片处理失败，区域: {region}")
                    continue
                
                # 保存文件
                filename = f"batch_{i:03d}_{int(time.time() * 1000)}.png"
                file_path = os.path.join(save_dir, filename)
                
                if self.screenshot_manager.save_screenshot(processed_data, file_path):
                    file_paths.append(file_path)
                    
                    # 记录历史
                    self._record_capture(
                        task_id=f"batch_{int(time.time())}",
                        screenshot_data=processed_data,
                        region=region,
                        file_path=file_path
                    )
                else:
                    self.logger.error(f"保存截图失败: {file_path}")
            
            self.logger.info(f"批量截图完成，成功: {len(file_paths)}/{len(regions)}")
            return file_paths
            
        except Exception as e:
            self.logger.error(f"批量截图失败: {e}")
            return []
    
    def get_history(self, limit: int = 100, task_id: Optional[str] = None,
                   start_time: Optional[float] = None, 
                   end_time: Optional[float] = None) -> List[Dict[str, Any]]:
        """获取截图历史记录
        
        Args:
            limit: 记录数量限制
            task_id: 任务ID过滤
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            List[Dict[str, Any]]: 历史记录列表
        """
        try:
            with self.history_lock:
                history = self.capture_history.copy()
            
            # 过滤
            if task_id:
                history = [record for record in history if record.get("task_id") == task_id]
            
            if start_time:
                history = [record for record in history if record.get("timestamp", 0) >= start_time]
            
            if end_time:
                history = [record for record in history if record.get("timestamp", 0) <= end_time]
            
            # 排序和限制
            history.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            
            return history[:limit]
            
        except Exception as e:
            self.logger.error(f"获取历史记录失败: {e}")
            return []
    
    def cleanup_old_files(self, days: Optional[int] = None) -> int:
        """清理旧截图文件
        
        Args:
            days: 保留天数，None表示使用配置中的值
            
        Returns:
            int: 清理的文件数量
        """
        try:
            if days is None:
                days = self.retention_config.get("screenshots", 7)
            
            cutoff_time = time.time() - (days * 24 * 3600)
            cleaned_count = 0
            
            # 遍历截图目录
            for root, dirs, files in os.walk(self.screenshot_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # 跳过历史文件
                    if file == "capture_history.json":
                        continue
                    
                    # 检查文件时间
                    if os.path.getmtime(file_path) < cutoff_time:
                        try:
                            os.remove(file_path)
                            cleaned_count += 1
                            self.logger.debug(f"删除旧截图文件: {file_path}")
                        except Exception as e:
                            self.logger.error(f"删除文件失败: {file_path}, 错误: {e}")
            
            self.logger.info(f"清理旧截图文件完成，删除: {cleaned_count} 个文件")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"清理旧文件失败: {e}")
            return 0
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息
        
        Returns:
            Dict[str, Any]: 性能统计信息
        """
        avg_capture_time = self.total_capture_time / self.total_captures if self.total_captures > 0 else 0
        success_rate = self.successful_captures / self.total_captures if self.total_captures > 0 else 0
        
        return {
            "total_captures": self.total_captures,
            "successful_captures": self.successful_captures,
            "failed_captures": self.failed_captures,
            "success_rate": success_rate,
            "total_capture_time": self.total_capture_time,
            "average_capture_time": avg_capture_time,
            "active_tasks": len(self.capture_tasks),
            "history_records": len(self.capture_history),
            "uptime": time.time() - self.start_time if self.start_time > 0 else 0
        }
    
    def _check_dependencies(self) -> bool:
        """检查依赖模块
        
        Returns:
            bool: 检查是否通过
        """
        try:
            if not self.screenshot_manager.is_initialized:
                self.logger.error("截图管理器未初始化")
                return False
            
            if not self.image_processor.is_initialized:
                self.logger.error("图片处理器未初始化")
                return False
            
            if not self.device_manager.check_device():
                self.logger.error("设备未连接")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"检查依赖模块失败: {e}")
            return False
    
    def _start_scheduler(self):
        """启动调度器"""
        try:
            self.is_running = True
            
            # 启动调度线程
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            
            # 启动工作线程
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            
            self.logger.info("截图调度器已启动")
            
        except Exception as e:
            self.logger.error(f"启动调度器失败: {e}")
    
    def _stop_scheduler(self):
        """停止调度器"""
        try:
            self.is_running = False
            
            # 等待线程结束
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            if self.worker_thread and self.worker_thread.is_alive():
                self.worker_thread.join(timeout=5)
            
            self.logger.info("截图调度器已停止")
            
        except Exception as e:
            self.logger.error(f"停止调度器失败: {e}")
    
    def _scheduler_loop(self):
        """调度器循环"""
        while self.is_running:
            try:
                current_time = time.time()
                
                with self.task_lock:
                    tasks_to_execute = []
                    
                    # 检查需要执行的任务
                    for task_id, task in list(self.capture_tasks.items()):
                        if current_time >= task.next_capture_time and task.current_count < task.count:
                            tasks_to_execute.append(task)
                            
                            # 更新下次执行时间
                            task.next_capture_time = current_time + task.interval
                            task.current_count += 1
                            
                            # 检查是否完成
                            if task.current_count >= task.count:
                                del self.capture_tasks[task_id]
                                self.logger.info(f"任务完成: {task_id}")
                    
                    # 添加到执行队列
                    for task in tasks_to_execute:
                        self.task_queue.put(task)
                
                # 短暂休眠
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"调度器循环错误: {e}")
                time.sleep(1)
    
    def _worker_loop(self):
        """工作线程循环"""
        while self.is_running:
            try:
                # 获取任务
                try:
                    task = self.task_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # 执行截图
                self._execute_capture_task(task)
                
                # 标记任务完成
                self.task_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"工作线程循环错误: {e}")
                time.sleep(1)
    
    def _execute_capture_task(self, task: CaptureTask):
        """执行截图任务
        
        Args:
            task: 截图任务
        """
        start_time = time.time()
        
        try:
            self.logger.debug(f"执行截图任务: {task.task_id}")
            
            # 截图
            screenshot_data = self.screenshot_manager.capture_screen(task.region)
            if not screenshot_data:
                self.logger.error(f"截图失败，任务: {task.task_id}")
                return
            
            # 处理图片
            processed_data = self._process_screenshot(
                screenshot_data, task.preprocess, task.compress
            )
            if not processed_data:
                self.logger.error(f"图片处理失败，任务: {task.task_id}")
                return
            
            # 保存文件
            file_path = None
            if task.auto_save:
                if task.save_path:
                    file_path = task.save_path
                else:
                    filename = f"{task.task_id}_{task.current_count}_{int(time.time() * 1000)}.png"
                    file_path = os.path.join(self.screenshot_dir, filename)
                
                if not self.screenshot_manager.save_screenshot(processed_data, file_path):
                    self.logger.error(f"保存截图失败: {file_path}")
                    return
            
            # 记录历史
            self._record_capture(
                task_id=task.task_id,
                screenshot_data=processed_data,
                region=task.region,
                file_path=file_path,
                processing_time=time.time() - start_time
            )
            
            # 执行回调
            if task.callback:
                try:
                    task.callback(processed_data, file_path)
                except Exception as e:
                    self.logger.error(f"回调执行失败: {e}")
            
            # 更新统计
            self.total_captures += 1
            self.successful_captures += 1
            self.total_capture_time += time.time() - start_time
            
            self.logger.debug(f"截图任务执行成功: {task.task_id}")
            
        except Exception as e:
            self.logger.error(f"执行截图任务失败: {task.task_id}, 错误: {e}")
            
            # 更新统计
            self.total_captures += 1
            self.failed_captures += 1
    
    def _process_screenshot(self, screenshot_data: bytes, preprocess: bool, compress: bool) -> Optional[bytes]:
        """处理截图
        
        Args:
            screenshot_data: 原始截图数据
            preprocess: 是否预处理
            compress: 是否压缩
            
        Returns:
            Optional[bytes]: 处理后的截图数据
        """
        try:
            processed_data = screenshot_data
            
            # 预处理
            if preprocess:
                processed_data = self.image_processor.preprocess_image(processed_data)
                if not processed_data:
                    return None
            
            # 压缩
            if compress:
                processed_data = self.image_processor.optimize_image(processed_data)
                if not processed_data:
                    return None
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"处理截图失败: {e}")
            return None
    
    def _record_capture(self, task_id: str, screenshot_data: bytes, 
                       region: Optional[Tuple[int, int, int, int]], 
                       file_path: Optional[str] = None, processing_time: float = 0):
        """记录截图历史
        
        Args:
            task_id: 任务ID
            screenshot_data: 截图数据
            region: 截图区域
            file_path: 文件路径
            processing_time: 处理时间
        """
        try:
            # 获取图片信息
            image_info = self.image_processor.get_image_info(screenshot_data)
            if not image_info:
                return
            
            # 创建记录
            record = CaptureRecord(
                record_id=f"record_{int(time.time() * 1000)}_{self.total_captures}",
                task_id=task_id,
                timestamp=time.time(),
                file_path=file_path,
                file_size=len(screenshot_data),
                width=image_info.get("width", 0),
                height=image_info.get("height", 0),
                format=image_info.get("format", "Unknown"),
                region=region,
                processing_time=processing_time,
                success=True
            )
            
            # 添加到历史记录
            with self.history_lock:
                self.capture_history.append(asdict(record))
                
                # 限制历史记录数量
                max_records = self.retention_config.get("maxRecords", 10000)
                if len(self.capture_history) > max_records:
                    self.capture_history = self.capture_history[-max_records:]
            
            # 定期保存历史记录
            if len(self.capture_history) % 10 == 0:
                self._save_history()
            
        except Exception as e:
            self.logger.error(f"记录截图历史失败: {e}")
    
    def _load_history(self):
        """加载历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.capture_history = json.load(f)
                
                self.logger.info(f"加载截图历史记录: {len(self.capture_history)} 条")
            else:
                self.capture_history = []
                
        except Exception as e:
            self.logger.error(f"加载历史记录失败: {e}")
            self.capture_history = []
    
    def _save_history(self):
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.capture_history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"保存历史记录失败: {e}")
    
    def _cleanup_expired_records(self):
        """清理过期记录"""
        try:
            days = self.retention_config.get("screenshots", 7)
            cutoff_time = time.time() - (days * 24 * 3600)
            
            with self.history_lock:
                original_count = len(self.capture_history)
                self.capture_history = [
                    record for record in self.capture_history
                    if record.get("timestamp", 0) >= cutoff_time
                ]
                
                cleaned_count = original_count - len(self.capture_history)
                if cleaned_count > 0:
                    self.logger.info(f"清理过期历史记录: {cleaned_count} 条")
            
        except Exception as e:
            self.logger.error(f"清理过期记录失败: {e}")
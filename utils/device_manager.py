#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备管理器
负责管理与Android设备的通信和操作
"""

import os
import time
import json
import subprocess
from typing import Dict, Any, Optional, List


class DeviceManager:
    """设备管理器类"""
    
    def __init__(self, config_manager, logger):
        """初始化设备管理器
        
        Args:
            config_manager: 配置管理器实例
            logger: 日志记录器实例
        """
        self.config_manager = config_manager
        self.logger = logger
        
        # 设备配置
        self.device_config = config_manager.get("device", {})
        self.device_id = self.device_config.get("deviceId", "")
        self.adb_path = self.device_config.get("adbPath", "adb")
        self.connection_timeout = self.device_config.get("connectionTimeout", 30)
        
        # 设备信息缓存
        self.device_info = {}
        self.last_check_time = 0
    
    def check_device(self) -> bool:
        """检查设备连接状态
        
        Returns:
            bool: 设备是否连接
        """
        try:
            self.logger.info("检查设备连接状态")
            
            # 检查adb是否可用
            if not self._check_adb_available():
                self.logger.error("ADB不可用")
                return False
            
            # 获取设备列表
            devices = self._get_connected_devices()
            if not devices:
                self.logger.error("没有连接的设备")
                return False
            
            # 检查指定设备
            if self.device_id:
                if self.device_id not in devices:
                    self.logger.error(f"指定设备未连接: {self.device_id}")
                    return False
            else:
                # 使用第一个设备
                self.device_id = devices[0]
                self.logger.info(f"使用设备: {self.device_id}")
            
            # 检查设备是否响应
            if not self._check_device_responsive():
                self.logger.error("设备无响应")
                return False
            
            # 获取设备信息
            self._update_device_info()
            
            self.logger.info("设备检查通过")
            return True
            
        except Exception as e:
            self.logger.error(f"设备检查失败: {e}")
            return False
    
    def get_device_info(self) -> Dict[str, Any]:
        """获取设备信息
        
        Returns:
            Dict[str, Any]: 设备信息
        """
        # 缓存5分钟
        if time.time() - self.last_check_time > 300:
            self._update_device_info()
        
        return self.device_info
    
    def push_file(self, local_path: str, remote_path: str) -> bool:
        """推送文件到设备
        
        Args:
            local_path: 本地文件路径
            remote_path: 设备文件路径
            
        Returns:
            bool: 推送是否成功
        """
        try:
            self.logger.info(f"推送文件到设备: {local_path} -> {remote_path}")
            
            # 检查本地文件是否存在
            if not os.path.exists(local_path):
                self.logger.error(f"本地文件不存在: {local_path}")
                return False
            
            # 创建远程目录
            remote_dir = os.path.dirname(remote_path)
            if remote_dir:
                self._run_adb_command(f"shell mkdir -p {remote_dir}")
            
            # 推送文件
            result = self._run_adb_command(f"push {local_path} {remote_path}")
            if result != 0:
                self.logger.error(f"推送文件失败: {local_path}")
                return False
            
            self.logger.info(f"文件推送成功: {local_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"推送文件失败: {e}")
            return False
    
    def pull_file(self, remote_path: str, local_path: str) -> bool:
        """从设备拉取文件
        
        Args:
            remote_path: 设备文件路径
            local_path: 本地文件路径
            
        Returns:
            bool: 拉取是否成功
        """
        try:
            self.logger.info(f"从设备拉取文件: {remote_path} -> {local_path}")
            
            # 创建本地目录
            local_dir = os.path.dirname(local_path)
            if local_dir:
                os.makedirs(local_dir, exist_ok=True)
            
            # 拉取文件
            result = self._run_adb_command(f"pull {remote_path} {local_path}")
            if result != 0:
                self.logger.error(f"拉取文件失败: {remote_path}")
                return False
            
            self.logger.info(f"文件拉取成功: {remote_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"拉取文件失败: {e}")
            return False
    
    def execute_command(self, command: str, timeout: int = 30) -> Optional[str]:
        """在设备上执行命令
        
        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            
        Returns:
            Optional[str]: 命令输出
        """
        try:
            self.logger.debug(f"在设备上执行命令: {command}")
            
            # 构建adb命令
            adb_command = f"shell {command}"
            if self.device_id:
                adb_command = f"-s {self.device_id} {adb_command}"
            
            # 执行命令
            result = subprocess.run(
                [self.adb_path] + adb_command.split(),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                self.logger.error(f"命令执行失败: {command}, 错误: {result.stderr}")
                return None
            
            output = result.stdout.strip()
            self.logger.debug(f"命令输出: {output}")
            return output
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"命令执行超时: {command}")
            return None
        except Exception as e:
            self.logger.error(f"命令执行失败: {e}")
            return None
    
    def get_device_logs(self, filter_pattern: str = "MarketAutomation") -> List[str]:
        """获取设备日志
        
        Args:
            filter_pattern: 日志过滤模式
            
        Returns:
            List[str]: 日志行列表
        """
        try:
            self.logger.debug(f"获取设备日志，过滤: {filter_pattern}")
            
            # 使用logcat获取日志
            command = f"logcat -d -s {filter_pattern}"
            output = self.execute_command(command)
            
            if not output:
                return []
            
            # 分割日志行
            log_lines = output.split('\n')
            
            # 过滤空行
            log_lines = [line.strip() for line in log_lines if line.strip()]
            
            self.logger.debug(f"获取到 {len(log_lines)} 条日志")
            return log_lines
            
        except Exception as e:
            self.logger.error(f"获取设备日志失败: {e}")
            return []
    
    def collect_data(self) -> Optional[List[Dict[str, Any]]]:
        """从设备收集数据
        
        Returns:
            Optional[List[Dict[str, Any]]]: 收集到的数据
        """
        try:
            self.logger.info("从设备收集数据")
            
            # 收集市场数据文件
            data_files = [
                "/data/data/com.cyjh.elfin/market_data.json",
                "/data/data/com.cyjh.elfin/market_report_*.json"
            ]
            
            all_data = []
            
            for file_pattern in data_files:
                # 获取匹配的文件列表
                if '*' in file_pattern:
                    # 处理通配符
                    command = f"find $(dirname {file_pattern}) -name \"$(basename {file_pattern})\""
                    files = self.execute_command(command)
                    if files:
                        file_list = files.split('\n')
                    else:
                        file_list = []
                else:
                    file_list = [file_pattern]
                
                # 读取每个文件
                for file_path in file_list:
                    if file_path.strip():
                        content = self.execute_command(f"cat {file_path}")
                        if content:
                            try:
                                data = json.loads(content)
                                if isinstance(data, list):
                                    all_data.extend(data)
                                else:
                                    all_data.append(data)
                            except json.JSONDecodeError:
                                self.logger.warning(f"无法解析数据文件: {file_path}")
            
            self.logger.info(f"收集到 {len(all_data)} 条数据")
            return all_data if all_data else None
            
        except Exception as e:
            self.logger.error(f"收集数据失败: {e}")
            return None
    
    def _check_adb_available(self) -> bool:
        """检查ADB是否可用
        
        Returns:
            bool: ADB是否可用
        """
        try:
            result = subprocess.run(
                [self.adb_path, "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_connected_devices(self) -> List[str]:
        """获取连接的设备列表
        
        Returns:
            List[str]: 设备ID列表
        """
        try:
            result = subprocess.run(
                [self.adb_path, "devices"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
            devices = []
            
            for line in lines:
                parts = line.split('\t')
                if len(parts) >= 2 and parts[1] == 'device':
                    devices.append(parts[0])
            
            return devices
            
        except Exception:
            return []
    
    def _check_device_responsive(self) -> bool:
        """检查设备是否响应
        
        Returns:
            bool: 设备是否响应
        """
        try:
            # 尝试获取设备属性
            output = self.execute_command("getprop ro.product.model", timeout=10)
            return output is not None
        except Exception:
            return False
    
    def _update_device_info(self):
        """更新设备信息"""
        try:
            self.logger.debug("更新设备信息")
            
            device_info = {}
            
            # 获取基本信息
            device_info['model'] = self.execute_command("getprop ro.product.model") or "Unknown"
            device_info['manufacturer'] = self.execute_command("getprop ro.product.manufacturer") or "Unknown"
            device_info['android_version'] = self.execute_command("getprop ro.build.version.release") or "Unknown"
            device_info['api_level'] = self.execute_command("getprop ro.build.version.sdk") or "Unknown"
            
            # 获取屏幕分辨率
            wm_size = self.execute_command("wm size")
            if wm_size and "Physical size:" in wm_size:
                size_part = wm_size.split("Physical size:")[1].strip()
                device_info['screen_resolution'] = size_part
            
            # 获取设备ID
            device_info['device_id'] = self.device_id
            
            # 获取时间戳
            device_info['last_update'] = time.time()
            
            self.device_info = device_info
            self.last_check_time = time.time()
            
        except Exception as e:
            self.logger.error(f"更新设备信息失败: {e}")
    
    def _run_adb_command(self, command: str) -> int:
        """运行ADB命令
        
        Args:
            command: ADB命令
            
        Returns:
            int: 返回码
        """
        try:
            full_command = f"{self.adb_path}"
            if self.device_id:
                full_command += f" -s {self.device_id}"
            full_command += f" {command}"
            
            result = subprocess.run(
                full_command.split(),
                capture_output=True,
                text=True,
                timeout=self.connection_timeout
            )
            
            return result.returncode
            
        except Exception as e:
            self.logger.error(f"运行ADB命令失败: {e}")
            return -1
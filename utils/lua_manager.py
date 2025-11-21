#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lua管理器
负责管理Lua脚本的执行和通信
"""

import os
import time
import json
import threading
from typing import Dict, Any, Optional, List


class LuaManager:
    """Lua管理器类"""
    
    def __init__(self, config_manager, logger):
        """初始化Lua管理器
        
        Args:
            config_manager: 配置管理器实例
            logger: 日志记录器实例
        """
        self.config_manager = config_manager
        self.logger = logger
        
        # Lua配置
        self.lua_config = config_manager.get("lua", {})
        self.script_path = self.lua_config.get("scriptPath", "/data/data/com.cyjh.elfin/scripts/market_automation.lua")
        self.auto_start = self.lua_config.get("autoStart", False)
        self.restart_on_error = self.lua_config.get("restartOnError", True)
        self.max_restart_attempts = self.lua_config.get("maxRestartAttempts", 3)
        self.script_timeout = self.lua_config.get("scriptTimeout", 300000)
        
        # 通信配置
        self.comm_file = self.lua_config.get("communication", {}).get("fridaCommFile", "/data/data/com.cyjh.elfin/frida_lua_comm.json")
        self.comm_check_interval = self.lua_config.get("communication", {}).get("commCheckInterval", 100)
        self.comm_timeout = self.lua_config.get("communication", {}).get("commTimeout", 5000)
        
        # 状态变量
        self.is_running = False
        self.is_paused = False
        self.restart_count = 0
        self.start_time = 0
        self.last_comm_time = 0
        
        # 线程锁
        self.lock = threading.Lock()
        
        # 监控线程
        self.monitor_thread = None
        self.comm_thread = None
    
    def start_script(self) -> bool:
        """启动Lua脚本
        
        Returns:
            bool: 启动是否成功
        """
        with self.lock:
            if self.is_running:
                self.logger.warning("Lua脚本已在运行")
                return True
            
            try:
                self.logger.info("启动Lua脚本")
                
                # 检查脚本文件是否存在
                if not self._check_script_exists():
                    self.logger.error(f"Lua脚本文件不存在: {self.script_path}")
                    return False
                
                # 启动脚本（这里需要根据实际情况实现）
                if not self._start_lua_process():
                    self.logger.error("启动Lua进程失败")
                    return False
                
                # 启动监控线程
                self._start_monitoring_threads()
                
                self.is_running = True
                self.is_paused = False
                self.start_time = time.time()
                self.restart_count = 0
                
                self.logger.info("Lua脚本启动成功")
                return True
                
            except Exception as e:
                self.logger.error(f"启动Lua脚本失败: {e}")
                return False
    
    def stop_script(self) -> bool:
        """停止Lua脚本
        
        Returns:
            bool: 停止是否成功
        """
        with self.lock:
            if not self.is_running:
                self.logger.warning("Lua脚本未运行")
                return True
            
            try:
                self.logger.info("停止Lua脚本")
                
                # 停止监控线程
                self._stop_monitoring_threads()
                
                # 停止Lua进程（这里需要根据实际情况实现）
                if not self._stop_lua_process():
                    self.logger.error("停止Lua进程失败")
                    return False
                
                self.is_running = False
                self.is_paused = False
                
                self.logger.info("Lua脚本已停止")
                return True
                
            except Exception as e:
                self.logger.error(f"停止Lua脚本失败: {e}")
                return False
    
    def pause_script(self) -> bool:
        """暂停Lua脚本
        
        Returns:
            bool: 暂停是否成功
        """
        with self.lock:
            if not self.is_running:
                self.logger.warning("Lua脚本未运行")
                return False
            
            if self.is_paused:
                self.logger.warning("Lua脚本已暂停")
                return True
            
            try:
                self.logger.info("暂停Lua脚本")
                
                # 发送暂停命令到Lua脚本
                if not self._send_command("pause"):
                    self.logger.error("发送暂停命令失败")
                    return False
                
                self.is_paused = True
                self.logger.info("Lua脚本已暂停")
                return True
                
            except Exception as e:
                self.logger.error(f"暂停Lua脚本失败: {e}")
                return False
    
    def resume_script(self) -> bool:
        """恢复Lua脚本
        
        Returns:
            bool: 恢复是否成功
        """
        with self.lock:
            if not self.is_running:
                self.logger.warning("Lua脚本未运行")
                return False
            
            if not self.is_paused:
                self.logger.warning("Lua脚本未暂停")
                return True
            
            try:
                self.logger.info("恢复Lua脚本")
                
                # 发送恢复命令到Lua脚本
                if not self._send_command("resume"):
                    self.logger.error("发送恢复命令失败")
                    return False
                
                self.is_paused = False
                self.logger.info("Lua脚本已恢复")
                return True
                
            except Exception as e:
                self.logger.error(f"恢复Lua脚本失败: {e}")
                return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取Lua脚本状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        return {
            "running": self.is_running,
            "paused": self.is_paused,
            "restart_count": self.restart_count,
            "start_time": self.start_time,
            "uptime": time.time() - self.start_time if self.is_running else 0,
            "script_path": self.script_path,
            "last_comm_time": self.last_comm_time
        }
    
    def send_command(self, command: str, params: Dict[str, Any] = None) -> bool:
        """发送命令到Lua脚本
        
        Args:
            command: 命令名称
            params: 命令参数
            
        Returns:
            bool: 发送是否成功
        """
        try:
            message = {
                "command": command,
                "params": params or {},
                "timestamp": time.time()
            }
            
            return self._send_message(message)
            
        except Exception as e:
            self.logger.error(f"发送命令失败: {e}")
            return False
    
    def _check_script_exists(self) -> bool:
        """检查脚本文件是否存在
        
        Returns:
            bool: 文件是否存在
        """
        # 这里需要根据实际情况实现
        # 可能需要通过adb检查设备上的文件
        return True
    
    def _start_lua_process(self) -> bool:
        """启动Lua进程
        
        Returns:
            bool: 启动是否成功
        """
        try:
            self.logger.info("启动Lua进程")
            
            # 这里需要根据实际情况实现
            # 可能需要通过adb在设备上执行Lua脚本
            # 例如: adb shell "lua /data/data/com.cyjh.elfin/scripts/market_automation.lua"
            
            # 等待脚本启动
            time.sleep(2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"启动Lua进程失败: {e}")
            return False
    
    def _stop_lua_process(self) -> bool:
        """停止Lua进程
        
        Returns:
            bool: 停止是否成功
        """
        try:
            self.logger.info("停止Lua进程")
            
            # 这里需要根据实际情况实现
            # 可能需要通过adb杀死Lua进程
            # 例如: adb shell "pkill -f market_automation.lua"
            
            return True
            
        except Exception as e:
            self.logger.error(f"停止Lua进程失败: {e}")
            return False
    
    def _send_command(self, command: str) -> bool:
        """发送命令到Lua脚本
        
        Args:
            command: 命令名称
            
        Returns:
            bool: 发送是否成功
        """
        try:
            # 通过通信文件发送命令
            message = {
                "type": "command",
                "command": command,
                "timestamp": time.time()
            }
            
            return self._send_message(message)
            
        except Exception as e:
            self.logger.error(f"发送命令失败: {e}")
            return False
    
    def _send_message(self, message: Dict[str, Any]) -> bool:
        """发送消息到Lua脚本
        
        Args:
            message: 消息内容
            
        Returns:
            bool: 发送是否成功
        """
        try:
            # 这里需要根据实际情况实现
            # 可能需要通过adb写入通信文件到设备
            # 例如: adb shell "echo '{json.dumps(message)}' > /data/data/com.cyjh.elfin/lua_command.json"
            
            self.logger.debug(f"发送消息: {message}")
            return True
            
        except Exception as e:
            self.logger.error(f"发送消息失败: {e}")
            return False
    
    def _start_monitoring_threads(self):
        """启动监控线程"""
        self.logger.info("启动Lua监控线程")
        
        # 启动脚本状态监控线程
        self.monitor_thread = threading.Thread(target=self._script_monitor, daemon=True)
        self.monitor_thread.start()
        
        # 启动通信监控线程
        self.comm_thread = threading.Thread(target=self._communication_monitor, daemon=True)
        self.comm_thread.start()
    
    def _stop_monitoring_threads(self):
        """停止监控线程"""
        self.logger.info("停止Lua监控线程")
        
        # 线程会在下一次循环时自动退出（因为self.is_running会变为False）
        # 这里可以添加更优雅的停止机制
    
    def _script_monitor(self):
        """脚本状态监控线程"""
        while self.is_running:
            try:
                # 检查脚本是否仍在运行
                if not self._check_script_running():
                    self.logger.warning("检测到Lua脚本停止运行")
                    
                    if self.restart_on_error and self.restart_count < self.max_restart_attempts:
                        self.logger.info(f"尝试重启Lua脚本 (第{self.restart_count + 1}次)")
                        self.restart_count += 1
                        
                        if self._restart_script():
                            self.logger.info("Lua脚本重启成功")
                        else:
                            self.logger.error("Lua脚本重启失败")
                    else:
                        self.logger.error("Lua脚本停止运行且无法重启")
                        self.is_running = False
                        break
                
                time.sleep(5)  # 每5秒检查一次
                
            except Exception as e:
                self.logger.error(f"脚本监控错误: {e}")
                time.sleep(10)
    
    def _communication_monitor(self):
        """通信监控线程"""
        while self.is_running:
            try:
                # 检查通信文件
                if self._check_communication_file():
                    self.last_comm_time = time.time()
                
                time.sleep(self.comm_check_interval / 1000)  # 转换为秒
                
            except Exception as e:
                self.logger.error(f"通信监控错误: {e}")
                time.sleep(1)
    
    def _check_script_running(self) -> bool:
        """检查脚本是否仍在运行
        
        Returns:
            bool: 脚本是否运行
        """
        # 这里需要根据实际情况实现
        # 可能需要通过adb检查Lua进程是否存在
        # 例如: adb shell "pgrep -f market_automation.lua"
        return True
    
    def _check_communication_file(self) -> bool:
        """检查通信文件
        
        Returns:
            bool: 是否有新的通信
        """
        try:
            # 这里需要根据实际情况实现
            # 可能需要通过adb读取设备上的通信文件
            # 例如: adb shell "cat /data/data/com.cyjh.elfin/frida_lua_comm.json"
            
            return False
            
        except Exception as e:
            self.logger.error(f"检查通信文件失败: {e}")
            return False
    
    def _restart_script(self) -> bool:
        """重启脚本
        
        Returns:
            bool: 重启是否成功
        """
        try:
            self.logger.info("重启Lua脚本")
            
            # 停止当前脚本
            self._stop_lua_process()
            
            # 等待一段时间
            time.sleep(2)
            
            # 重新启动脚本
            return self._start_lua_process()
            
        except Exception as e:
            self.logger.error(f"重启脚本失败: {e}")
            return False
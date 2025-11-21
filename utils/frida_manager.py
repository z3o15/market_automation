#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Frida管理器
负责管理Frida服务器和Hook脚本
"""

import os
import time
import json
import subprocess
import threading
from typing import Dict, Any, Optional, List

try:
    import frida
except ImportError:
    print("警告: 未安装frida库，请运行: pip install frida-tools")
    frida = None


class FridaManager:
    """Frida管理器类"""
    
    def __init__(self, config_manager, logger):
        """初始化Frida管理器
        
        Args:
            config_manager: 配置管理器实例
            logger: 日志记录器实例
        """
        self.config_manager = config_manager
        self.logger = logger
        
        # Frida配置
        self.frida_config = config_manager.get("frida", {})
        self.script_path = self.frida_config.get("scriptPath", "/data/local/tmp/market_hook.js")
        self.package_name = self.frida_config.get("packageName", "com.cyjh.elfin")
        self.spawn = self.frida_config.get("spawn", True)
        self.pause = self.frida_config.get("pause", False)
        self.runtime = self.frida_config.get("runtime", "v8")
        
        # 状态变量
        self.server_process = None
        self.session = None
        self.script = None
        self.device = None
        self.is_server_running = False
        self.is_script_injected = False
        
        # 线程锁
        self.lock = threading.Lock()
    
    def start_frida_server(self) -> bool:
        """启动Frida服务器
        
        Returns:
            bool: 启动是否成功
        """
        with self.lock:
            if self.is_server_running:
                self.logger.warning("Frida服务器已在运行")
                return True
            
            try:
                self.logger.info("启动Frida服务器")
                
                # 检查frida是否可用
                if frida is None:
                    self.logger.error("Frida库未安装")
                    return False
                
                # 获取设备
                self.device = self._get_device()
                if not self.device:
                    self.logger.error("无法获取设备")
                    return False
                
                # 启动frida-server（如果需要）
                if not self._check_frida_server():
                    if not self._start_frida_server_on_device():
                        self.logger.error("启动设备上的frida-server失败")
                        return False
                
                self.is_server_running = True
                self.logger.info("Frida服务器启动成功")
                return True
                
            except Exception as e:
                self.logger.error(f"启动Frida服务器失败: {e}")
                return False
    
    def stop_frida_server(self) -> bool:
        """停止Frida服务器
        
        Returns:
            bool: 停止是否成功
        """
        with self.lock:
            if not self.is_server_running:
                self.logger.warning("Frida服务器未运行")
                return True
            
            try:
                self.logger.info("停止Frida服务器")
                
                # 停止脚本
                if self.is_script_injected:
                    self.stop_script()
                
                # 停止服务器进程
                if self.server_process:
                    self.server_process.terminate()
                    self.server_process.wait()
                    self.server_process = None
                
                self.is_server_running = False
                self.logger.info("Frida服务器已停止")
                return True
                
            except Exception as e:
                self.logger.error(f"停止Frida服务器失败: {e}")
                return False
    
    def inject_script(self) -> bool:
        """注入Frida Hook脚本
        
        Returns:
            bool: 注入是否成功
        """
        with self.lock:
            if self.is_script_injected:
                self.logger.warning("Frida脚本已注入")
                return True
            
            if not self.is_server_running:
                self.logger.error("Frida服务器未运行")
                return False
            
            try:
                self.logger.info("注入Frida Hook脚本")
                
                # 检查脚本文件是否存在
                if not os.path.exists(self.script_path):
                    self.logger.error(f"脚本文件不存在: {self.script_path}")
                    return False
                
                # 读取脚本内容
                with open(self.script_path, 'r', encoding='utf-8') as f:
                    script_code = f.read()
                
                # 附加到目标进程
                if self.spawn:
                    # 启动新进程
                    self.logger.info(f"启动新进程: {self.package_name}")
                    pid = self.device.spawn([self.package_name])
                    self.session = self.device.attach(pid)
                    
                    if not self.pause:
                        self.device.resume(pid)
                else:
                    # 附加到现有进程
                    self.session = self.device.attach(self.package_name)
                
                # 加载脚本
                self.script = self.session.create_script(script_code, runtime=self.runtime)
                
                # 设置消息处理器
                self.script.on('message', self._on_message)
                self.script.on('destroyed', self._on_destroyed)
                
                # 加载脚本
                self.script.load()
                
                self.is_script_injected = True
                self.logger.info("Frida Hook脚本注入成功")
                return True
                
            except Exception as e:
                self.logger.error(f"注入Frida脚本失败: {e}")
                return False
    
    def stop_script(self) -> bool:
        """停止Frida Hook脚本
        
        Returns:
            bool: 停止是否成功
        """
        with self.lock:
            if not self.is_script_injected:
                self.logger.warning("Frida脚本未注入")
                return True
            
            try:
                self.logger.info("停止Frida Hook脚本")
                
                # 卸载脚本
                if self.script:
                    self.script.unload()
                    self.script = None
                
                # 断开会话
                if self.session:
                    self.session.detach()
                    self.session = None
                
                self.is_script_injected = False
                self.logger.info("Frida Hook脚本已停止")
                return True
                
            except Exception as e:
                self.logger.error(f"停止Frida脚本失败: {e}")
                return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取Frida状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        return {
            "server_running": self.is_server_running,
            "script_injected": self.is_script_injected,
            "device_connected": self.device is not None,
            "session_active": self.session is not None,
            "script_loaded": self.script is not None,
            "package_name": self.package_name,
            "script_path": self.script_path
        }
    
    def call_rpc(self, method: str, *args) -> Any:
        """调用RPC方法
        
        Args:
            method: RPC方法名
            *args: 方法参数
            
        Returns:
            Any: 方法返回值
        """
        if not self.is_script_injected or not self.script:
            self.logger.error("Frida脚本未注入")
            return None
        
        try:
            return self.script.exports[method](*args)
        except Exception as e:
            self.logger.error(f"调用RPC方法失败: {e}")
            return None
    
    def _get_device(self):
        """获取设备
        
        Returns:
            Device: Frida设备对象
        """
        try:
            # 获取USB设备
            devices = frida.enumerate_devices()
            usb_device = None
            
            for device in devices:
                if device.type == 'usb':
                    usb_device = device
                    break
            
            if usb_device:
                self.logger.info(f"使用USB设备: {usb_device.id}")
                return usb_device
            
            # 如果没有USB设备，使用本地设备
            local_device = frida.get_local_device()
            if local_device:
                self.logger.info("使用本地设备")
                return local_device
            
            self.logger.error("没有可用的设备")
            return None
            
        except Exception as e:
            self.logger.error(f"获取设备失败: {e}")
            return None
    
    def _check_frida_server(self) -> bool:
        """检查Frida服务器是否运行
        
        Returns:
            bool: 服务器是否运行
        """
        try:
            if not self.device:
                return False
            
            # 尝试枚举进程
            processes = self.device.enumerate_processes()
            return len(processes) > 0
            
        except Exception:
            return False
    
    def _start_frida_server_on_device(self) -> bool:
        """在设备上启动Frida服务器
        
        Returns:
            bool: 启动是否成功
        """
        try:
            self.logger.info("在设备上启动frida-server")
            
            # 这里需要根据实际情况实现
            # 可能需要推送frida-server二进制文件到设备并执行
            
            # 示例代码（需要根据实际情况调整）
            # subprocess.run(['adb', 'push', 'frida-server', '/data/local/tmp/'])
            # subprocess.run(['adb', 'shell', 'chmod', '+x', '/data/local/tmp/frida-server'])
            # subprocess.run(['adb', 'shell', '/data/local/tmp/frida-server', '-D'])
            
            # 等待服务器启动
            time.sleep(3)
            
            return self._check_frida_server()
            
        except Exception as e:
            self.logger.error(f"启动设备上的frida-server失败: {e}")
            return False
    
    def _on_message(self, message, data):
        """处理Frida脚本消息
        
        Args:
            message: 消息对象
            data: 附加数据
        """
        try:
            if message['type'] == 'send':
                payload = message['payload']
                self.logger.debug(f"收到Frida消息: {payload}")
                
                # 处理不同类型的消息
                if isinstance(payload, dict):
                    if payload.get('type') == 'log':
                        self.logger.info(f"Frida日志: {payload.get('message')}")
                    elif payload.get('type') == 'error':
                        self.logger.error(f"Frida错误: {payload.get('message')}")
                    elif payload.get('type') == 'data':
                        self._handle_data_message(payload)
                else:
                    self.logger.debug(f"Frida消息: {payload}")
            
            elif message['type'] == 'error':
                self.logger.error(f"Frida脚本错误: {message['stack']}")
                
        except Exception as e:
            self.logger.error(f"处理Frida消息失败: {e}")
    
    def _on_destroyed(self):
        """处理脚本销毁事件"""
        self.logger.warning("Frida脚本被销毁")
        self.is_script_injected = False
        self.script = None
    
    def _handle_data_message(self, payload: Dict[str, Any]):
        """处理数据消息
        
        Args:
            payload: 数据载荷
        """
        try:
            data_type = payload.get('data_type')
            data = payload.get('data')
            
            if data_type == 'market_data':
                self.logger.info(f"收到市场数据: {len(data) if isinstance(data, list) else 1} 条记录")
                # 这里可以进一步处理市场数据
            elif data_type == 'click_event':
                self.logger.debug(f"收到点击事件: {data}")
                # 这里可以进一步处理点击事件
            else:
                self.logger.debug(f"未知数据类型: {data_type}")
                
        except Exception as e:
            self.logger.error(f"处理数据消息失败: {e}")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市场自动化工具 - 主控制脚本
基于传商精灵4.3u的装备市场自动化控制
作者: AI助手
功能: 启动Frida Hook、加载Lua脚本、管理配置等
"""

import os
import sys
import json
import time
import signal
import argparse
import subprocess
import threading
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入自定义模块
try:
    from utils.config_manager import ConfigManager
    from utils.logger import Logger
    from utils.frida_manager import FridaManager
    from utils.lua_manager import LuaManager
    from utils.device_manager import DeviceManager
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有依赖模块都已正确安装")
    sys.exit(1)


class MarketAutomation:
    """市场自动化主控制类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化市场自动化工具
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认配置
        """
        self.config_path = config_path or os.path.join(PROJECT_ROOT, "config", "market_config.json")
        self.running = False
        self.paused = False
        
        # 初始化配置管理器
        self.config_manager = ConfigManager(self.config_path)
        
        # 初始化日志记录器
        log_config = self.config_manager.get("logging", {})
        self.logger = Logger(
            level=log_config.get("level", "INFO"),
            log_file=log_config.get("logPath", "market_automation.log"),
            max_file_size=log_config.get("maxFileSize", "10MB"),
            max_files=log_config.get("maxFiles", 5)
        )
        
        # 初始化组件管理器
        self.device_manager = DeviceManager(self.config_manager, self.logger)
        self.frida_manager = FridaManager(self.config_manager, self.logger)
        self.lua_manager = LuaManager(self.config_manager, self.logger)
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("市场自动化工具初始化完成")
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info(f"接收到信号 {signum}，正在停止工具...")
        self.stop()
    
    def start(self) -> bool:
        """启动市场自动化工具
        
        Returns:
            bool: 启动是否成功
        """
        if self.running:
            self.logger.warning("工具已在运行中")
            return False
        
        self.logger.info("启动市场自动化工具")
        
        try:
            # 1. 检查设备连接
            if not self.device_manager.check_device():
                self.logger.error("设备检查失败")
                return False
            
            # 2. 推送必要文件到设备
            if not self._push_files_to_device():
                self.logger.error("推送文件到设备失败")
                return False
            
            # 3. 启动Frida服务器
            if not self.frida_manager.start_frida_server():
                self.logger.error("启动Frida服务器失败")
                return False
            
            # 4. 注入Frida Hook脚本
            if not self.frida_manager.inject_script():
                self.logger.error("注入Frida Hook脚本失败")
                return False
            
            # 5. 启动Lua脚本
            if not self.lua_manager.start_script():
                self.logger.error("启动Lua脚本失败")
                return False
            
            # 6. 启动监控线程
            self._start_monitoring_threads()
            
            self.running = True
            self.logger.info("市场自动化工具启动成功")
            return True
            
        except Exception as e:
            self.logger.error(f"启动工具时发生错误: {e}")
            return False
    
    def stop(self) -> bool:
        """停止市场自动化工具
        
        Returns:
            bool: 停止是否成功
        """
        if not self.running:
            self.logger.warning("工具未在运行")
            return False
        
        self.logger.info("停止市场自动化工具")
        
        try:
            # 停止Lua脚本
            self.lua_manager.stop_script()
            
            # 停止Frida Hook
            self.frida_manager.stop_script()
            
            # 停止Frida服务器
            self.frida_manager.stop_frida_server()
            
            self.running = False
            self.logger.info("市场自动化工具已停止")
            return True
            
        except Exception as e:
            self.logger.error(f"停止工具时发生错误: {e}")
            return False
    
    def pause(self) -> bool:
        """暂停市场自动化工具
        
        Returns:
            bool: 暂停是否成功
        """
        if not self.running:
            self.logger.warning("工具未在运行")
            return False
        
        if self.paused:
            self.logger.warning("工具已暂停")
            return False
        
        self.logger.info("暂停市场自动化工具")
        
        try:
            # 暂停Lua脚本
            self.lua_manager.pause_script()
            self.paused = True
            self.logger.info("工具已暂停")
            return True
            
        except Exception as e:
            self.logger.error(f"暂停工具时发生错误: {e}")
            return False
    
    def resume(self) -> bool:
        """恢复市场自动化工具
        
        Returns:
            bool: 恢复是否成功
        """
        if not self.running:
            self.logger.warning("工具未在运行")
            return False
        
        if not self.paused:
            self.logger.warning("工具未暂停")
            return False
        
        self.logger.info("恢复市场自动化工具")
        
        try:
            # 恢复Lua脚本
            self.lua_manager.resume_script()
            self.paused = False
            self.logger.info("工具已恢复")
            return True
            
        except Exception as e:
            self.logger.error(f"恢复工具时发生错误: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取工具状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        status = {
            "running": self.running,
            "paused": self.paused,
            "device": self.device_manager.get_device_info(),
            "frida": self.frida_manager.get_status(),
            "lua": self.lua_manager.get_status(),
            "uptime": time.time() - getattr(self, 'start_time', time.time())
        }
        return status
    
    def _push_files_to_device(self) -> bool:
        """推送必要文件到设备
        
        Returns:
            bool: 推送是否成功
        """
        self.logger.info("推送文件到设备")
        
        try:
            # 推送Frida脚本
            frida_script_path = os.path.join(PROJECT_ROOT, "scripts", "market_hook.js")
            device_frida_path = "/data/local/tmp/market_hook.js"
            
            if not self.device_manager.push_file(frida_script_path, device_frida_path):
                self.logger.error("推送Frida脚本失败")
                return False
            
            # 推送Lua脚本
            lua_script_path = os.path.join(PROJECT_ROOT, "scripts", "market_automation.lua")
            device_lua_path = "/data/data/com.cyjh.elfin/scripts/market_automation.lua"
            
            if not self.device_manager.push_file(lua_script_path, device_lua_path):
                self.logger.error("推送Lua脚本失败")
                return False
            
            # 推送配置文件
            lua_config_path = os.path.join(PROJECT_ROOT, "config", "lua_config.json")
            device_config_path = "/data/data/com.cyjh.elfin/lua_config.json"
            
            if not self.device_manager.push_file(lua_config_path, device_config_path):
                self.logger.error("推送Lua配置文件失败")
                return False
            
            self.logger.info("文件推送完成")
            return True
            
        except Exception as e:
            self.logger.error(f"推送文件时发生错误: {e}")
            return False
    
    def _start_monitoring_threads(self):
        """启动监控线程"""
        self.logger.info("启动监控线程")
        
        # 启动状态监控线程
        self.status_thread = threading.Thread(target=self._status_monitor, daemon=True)
        self.status_thread.start()
        
        # 启动日志监控线程
        self.log_thread = threading.Thread(target=self._log_monitor, daemon=True)
        self.log_thread.start()
        
        # 启动数据收集线程
        self.data_thread = threading.Thread(target=self._data_collector, daemon=True)
        self.data_thread.start()
    
    def _status_monitor(self):
        """状态监控线程"""
        while self.running:
            try:
                status = self.get_status()
                self.logger.debug(f"工具状态: {json.dumps(status, indent=2)}")
                time.sleep(30)  # 每30秒检查一次状态
            except Exception as e:
                self.logger.error(f"状态监控错误: {e}")
                time.sleep(10)
    
    def _log_monitor(self):
        """日志监控线程"""
        while self.running:
            try:
                # 从设备拉取日志
                device_logs = self.device_manager.get_device_logs()
                if device_logs:
                    for log_entry in device_logs:
                        self.logger.info(f"设备日志: {log_entry}")
                time.sleep(60)  # 每60秒检查一次日志
            except Exception as e:
                self.logger.error(f"日志监控错误: {e}")
                time.sleep(30)
    
    def _data_collector(self):
        """数据收集线程"""
        while self.running:
            try:
                # 从设备收集数据
                data = self.device_manager.collect_data()
                if data:
                    self.logger.info(f"收集到数据: {len(data)} 条记录")
                    # 处理收集到的数据
                    self._process_collected_data(data)
                time.sleep(300)  # 每5分钟收集一次数据
            except Exception as e:
                self.logger.error(f"数据收集错误: {e}")
                time.sleep(60)
    
    def _process_collected_data(self, data: List[Dict[str, Any]]):
        """处理收集到的数据
        
        Args:
            data: 收集到的数据列表
        """
        try:
            # 保存数据到本地
            data_dir = os.path.join(PROJECT_ROOT, "data")
            os.makedirs(data_dir, exist_ok=True)
            
            timestamp = int(time.time())
            data_file = os.path.join(data_dir, f"market_data_{timestamp}.json")
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"数据已保存到: {data_file}")
            
        except Exception as e:
            self.logger.error(f"处理数据时发生错误: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="市场自动化工具")
    parser.add_argument("--config", "-c", help="配置文件路径")
    parser.add_argument("--start", action="store_true", help="启动工具")
    parser.add_argument("--stop", action="store_true", help="停止工具")
    parser.add_argument("--pause", action="store_true", help="暂停工具")
    parser.add_argument("--resume", action="store_true", help="恢复工具")
    parser.add_argument("--status", action="store_true", help="查看状态")
    parser.add_argument("--daemon", "-d", action="store_true", help="以守护进程模式运行")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 创建市场自动化实例
    automation = MarketAutomation(args.config)
    
    # 设置日志级别
    if args.verbose:
        automation.logger.set_level("DEBUG")
    
    # 执行相应操作
    if args.start:
        if automation.start():
            if not args.daemon:
                try:
                    while automation.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    automation.stop()
        else:
            sys.exit(1)
    
    elif args.stop:
        if automation.stop():
            print("工具已停止")
        else:
            print("停止工具失败")
            sys.exit(1)
    
    elif args.pause:
        if automation.pause():
            print("工具已暂停")
        else:
            print("暂停工具失败")
            sys.exit(1)
    
    elif args.resume:
        if automation.resume():
            print("工具已恢复")
        else:
            print("恢复工具失败")
            sys.exit(1)
    
    elif args.status:
        status = automation.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
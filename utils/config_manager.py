#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
负责加载和管理配置文件
"""

import os
import json
import logging
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器类"""
    
    def __init__(self, config_path: str):
        """初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self) -> bool:
        """加载配置文件
        
        Returns:
            bool: 加载是否成功
        """
        try:
            if not os.path.exists(self.config_path):
                self.config = self._create_default_config()
                self.save_config()
                return True
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            return True
        except Exception as e:
            logging.error(f"加载配置文件失败: {e}")
            self.config = self._create_default_config()
            return False
    
    def save_config(self) -> bool:
        """保存配置文件
        
        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            
            return True
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
        except Exception:
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """设置配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
            
        Returns:
            bool: 设置是否成功
        """
        try:
            keys = key.split('.')
            config = self.config
            
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            config[keys[-1]] = value
            return True
        except Exception as e:
            logging.error(f"设置配置值失败: {e}")
            return False
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """批量更新配置
        
        Args:
            updates: 更新的配置字典
            
        Returns:
            bool: 更新是否成功
        """
        try:
            for key, value in updates.items():
                self.set(key, value)
            return True
        except Exception as e:
            logging.error(f"批量更新配置失败: {e}")
            return False
    
    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置
        
        Returns:
            Dict[str, Any]: 默认配置字典
        """
        return {
            "automation": {
                "clickDelay": {
                    "min": 300,
                    "max": 800,
                    "default": 500
                },
                "scrollDelay": {
                    "min": 1500,
                    "max": 2500,
                    "default": 2000
                },
                "maxRetries": 3,
                "retryDelay": 1000,
                "scrollInterval": 2000,
                "maxScrollCount": 10,
                "maxPages": 10,
                "itemsPerPage": 20,
                "pauseBetweenPages": 3000
            },
            "market": {
                "apiEndpoints": [
                    "https://api.example.com/market/equipment",
                    "https://backup.example.com/market/equipment"
                ],
                "requestTimeout": 10000,
                "retryInterval": 5000,
                "maxConcurrentRequests": 3,
                "cacheTimeout": 300000,
                "refreshInterval": 60000
            },
            "equipment": {
                "targetTypes": ["weapon", "armor", "accessory", "consumable"],
                "priceRange": {
                    "min": 100,
                    "max": 50000
                },
                "qualityLevels": ["common", "rare", "epic", "legendary"],
                "levelRange": {
                    "min": 1,
                    "max": 100
                },
                "excludeKeywords": ["破损", "损坏", "过期"],
                "includeKeywords": ["强化", "精炼", "稀有"]
            },
            "detection": {
                "antiDetection": {
                    "randomizeClicks": True,
                    "humanLikeMovement": True,
                    "variableTiming": True,
                    "randomScrollSpeed": True,
                    "simulateErrors": False,
                    "errorRate": 0.05
                },
                "stealthMode": True,
                "hideRoot": True,
                "hideDebug": True,
                "mimicHumanBehavior": True
            },
            "network": {
                "userAgent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36",
                "headers": {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest"
                },
                "proxy": {
                    "enabled": False,
                    "host": "",
                    "port": 0,
                    "username": "",
                    "password": ""
                },
                "sslVerification": True,
                "connectionTimeout": 15000,
                "readTimeout": 30000
            },
            "ui": {
                "screenResolution": {
                    "width": 1080,
                    "height": 1920
                },
                "clickOffset": {
                    "x": 5,
                    "y": 5
                },
                "scrollSpeed": {
                    "min": 500,
                    "max": 1500
                },
                "waitAfterClick": 200,
                "waitAfterScroll": 1000,
                "elementDetectionTimeout": 5000
            },
            "data": {
                "storage": {
                    "type": "sqlite",
                    "path": "/data/data/com.cyjh.elfin/market_data.db",
                    "backupPath": "/data/data/com.cyjh.elfin/market_data_backup.db"
                },
                "export": {
                    "format": "json",
                    "compression": True,
                    "autoExport": True,
                    "exportInterval": 3600000
                },
                "retention": {
                    "days": 30,
                    "maxRecords": 10000
                }
            },
            "logging": {
                "level": "INFO",
                "maxFileSize": "10MB",
                "maxFiles": 5,
                "enableRemoteLogging": False,
                "remoteEndpoint": "",
                "logToFile": True,
                "logPath": "/data/data/com.cyjh.elfin/market_automation.log",
                "logRotation": True,
                "enableDebugLog": False
            },
            "performance": {
                "maxMemoryUsage": 512,
                "gcInterval": 300000,
                "threadPoolSize": 4,
                "enableProfiling": False,
                "cacheSize": 1000,
                "batchSize": 50
            },
            "security": {
                "encryptData": True,
                "encryptionKey": "",
                "salt": "",
                "hashAlgorithm": "SHA-256",
                "enableAuthentication": False,
                "apiKey": "",
                "apiSecret": ""
            },
            "notification": {
                "enableEmail": False,
                "emailSettings": {
                    "smtp": "",
                    "port": 587,
                    "username": "",
                    "password": "",
                    "to": ""
                },
                "enablePush": False,
                "pushSettings": {
                    "service": "",
                    "apiKey": "",
                    "deviceToken": ""
                },
                "enableSound": True,
                "soundFile": "/system/media/audio/notifications/Notification.ogg"
            },
            "advanced": {
                "experimentalFeatures": False,
                "betaFeatures": False,
                "customHooks": [],
                "luaScripts": [],
                "plugins": [],
                "debugMode": False,
                "verboseLogging": False
            }
        }
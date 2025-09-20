#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
负责应用程序配置的加载、保存和管理
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """配置管理器类"""
    
    def __init__(self, config_file: str = "config/app_config.json"):
        self.config_file = config_file
        self.config_data = {}
        self._load_default_config()
        self.load_config()
    
    def _load_default_config(self):
        """加载默认配置"""
        self.config_data = {
            "app": {
                "name": "AI末日生存求生向导",
                "version": "1.0.0",
                "window_width": 1200,
                "window_height": 800,
                "theme": "light",
                "language": "zh_CN"
            },
            "database": {
                "path": "data/survival_guide.db",
                "backup_enabled": True,
                "backup_interval": 24  # 小时
            },
            "ai": {
                "model_type": "rule_based",
                "confidence_threshold": 0.7,
                "max_response_length": 500,
                "enable_learning": True
            },
            "ui": {
                "font_family": "Microsoft YaHei",
                "font_size": 12,
                "show_tips": True,
                "auto_save": True,
                "animation_enabled": True
            },
            "features": {
                "emergency_mode": True,
                "offline_mode": True,
                "voice_enabled": False,
                "notifications": True
            }
        }
    
    def load_config(self) -> bool:
        """从文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并配置，保留默认值
                    self._merge_config(self.config_data, loaded_config)
                return True
            else:
                # 配置文件不存在，创建默认配置文件
                self.save_config()
                return True
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return False
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            # 确保配置目录存在
            Path(self.config_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key_path: 配置键路径，如 'app.name' 或 'ui.font_size'
            default: 默认值
        
        Returns:
            配置值
        """
        try:
            keys = key_path.split('.')
            value = self.config_data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
        except Exception:
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """设置配置值
        
        Args:
            key_path: 配置键路径
            value: 配置值
        
        Returns:
            是否设置成功
        """
        try:
            keys = key_path.split('.')
            config = self.config_data
            
            # 导航到最后一级的父级
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # 设置值
            config[keys[-1]] = value
            return True
        except Exception as e:
            print(f"设置配置值失败: {e}")
            return False
    
    def _merge_config(self, default: Dict, loaded: Dict):
        """合并配置，保留默认值"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(default[key], dict) and isinstance(value, dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
            else:
                default[key] = value
    
    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config_data.copy()
    
    def reset_to_default(self) -> bool:
        """重置为默认配置"""
        try:
            self._load_default_config()
            return self.save_config()
        except Exception as e:
            print(f"重置配置失败: {e}")
            return False
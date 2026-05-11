"""
配置管理模块
负责程序配置的读取、保存和验证
"""

import json
import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime


def get_config_dir():
    """获取配置目录，兼容PyInstaller打包"""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        config_dir = os.path.join(base_dir, "config")
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    else:
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_dir = os.path.join(app_dir, "config")
        os.makedirs(config_dir, exist_ok=True)
        return config_dir


class ConfigManager:
    """配置管理器类"""

    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "paths": {
            "video_input": "./videos",
            "output_dir": "./output",
            "ffmpeg_path": "C:\\Users\\liket\\AppData\\Roaming\\TRAE SOLO CN\\ModularData\\ai-agent\\vm\\tools\\app\\ffmpeg\\ffmpeg.exe",
            "ffprobe_path": "C:\\Users\\liket\\AppData\\Roaming\\TRAE SOLO CN\\ModularData\\ai-agent\\vm\\tools\\app\\ffmpeg\\ffprobe.exe",
            "python_path": ""
        },
        "ocr": {
            "lang": "japan",
            "use_gpu": True,
            "enable_mkldnn": False,
            "det_db_thresh": 0.3,
            "det_db_box_thresh": 0.5,
            "rec_score_thresh": 0.5,
            "frame_interval": 1,
            "frame_quality": 2
        },
        "subtitle": {
            "min_length": 2,
            "max_gap": 3.0,
            "max_duration": 30.0,
            "similarity_threshold": 0.8
        },
        "translation": {
            "framework": "ollama",
            "ollama": {
                "host": "http://localhost:11434",
                "model": "quantumcookie/sakura-galtransl-v3.7:7b",
                "timeout": 120,
                "max_retries": 3,
                "temperature": 0.3
            },
            "lmstudio": {
                "host": "http://localhost:1234/v1",
                "model": "sakura-galtransl-v3.7",
                "timeout": 120,
                "max_retries": 3,
                "temperature": 0.3
            }
        },
        "ass_style": {
            "font_name": "Microsoft YaHei",
            "font_size": 20,
            "primary_color": "&H00FFFFFF",
            "outline_color": "&H00000000",
            "outline_width": 2,
            "shadow": 1,
            "margin_v": 30
        },
        "burn": {
            "preset": "p4",
            "crf": 23
        },
        "processing": {
            "auto_skip_processed": True,
            "wait_between_videos": 60,
            "cleanup_temp": True
        },
        "ui": {
            "theme": "default",
            "font_size": 27,
            "log_font_size": 27,
            "log_max_lines": 1000,
            "progress_update_interval": 1000,
            "window_width": 1200,
            "window_height": 800
        }
    }

    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = get_config_dir()
        self.config_dir = config_dir
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self) -> bool:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                self.config = self._merge_config(self.DEFAULT_CONFIG, loaded_config)
                return True
            except Exception as e:
                print(f"加载配置失败: {e}")
                self.config = self.DEFAULT_CONFIG.copy()
                return False
        else:
            self.config = self.DEFAULT_CONFIG.copy()
            self.save()
            return True

    def save(self) -> bool:
        """保存配置文件"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def _merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """合并配置，确保所有键都存在"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, key_path: str, default: Any = None) -> Any:
        """获取配置值，支持点分隔路径"""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, key_path: str, value: Any) -> bool:
        """设置配置值，支持点分隔路径"""
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        return True

    def validate_paths(self) -> Dict[str, bool]:
        """验证关键路径是否存在"""
        validation = {}
        path_keys = [
            'paths.ffmpeg_path',
            'paths.ffprobe_path',
            'paths.python_path'
        ]
        for key in path_keys:
            path = self.get(key)
            validation[key] = os.path.exists(path) if path else False
        return validation

    def get_ocr_config(self) -> Dict[str, Any]:
        """获取OCR配置"""
        return self.config.get('ocr', {})

    def get_translation_config(self) -> Dict[str, Any]:
        """获取翻译配置"""
        trans_config = self.config.get('translation', {})
        framework = trans_config.get('framework', 'ollama')
        framework_config = trans_config.get(framework, {})
        result = {
            'framework': framework,
            'host': framework_config.get('host', ''),
            'model': framework_config.get('model', ''),
            'timeout': framework_config.get('timeout', 120),
            'max_retries': framework_config.get('max_retries', 3),
            'temperature': framework_config.get('temperature', 0.3)
        }
        return result

    def get_ass_config(self) -> Dict[str, Any]:
        """获取ASS字幕样式配置"""
        return self.config.get('ass_style', {})

    def get_burn_config(self) -> Dict[str, Any]:
        """获取烧录配置"""
        return self.config.get('burn', {})

    def reset_to_default(self) -> bool:
        """重置为默认配置"""
        self.config = self.DEFAULT_CONFIG.copy()
        return self.save()

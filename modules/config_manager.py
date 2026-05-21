"""
配置管理模块
负责程序配置的读取、保存和验证
"""

import json
import os
import sys
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from .logger import logger


class ConfigKeys:
    """配置键常量定义"""
    
    # 路径配置
    PATH_VIDEO_INPUT = 'paths.video_input'
    PATH_OUTPUT_DIR = 'paths.output_dir'
    PATH_FFMPEG = 'paths.ffmpeg_path'
    PATH_FFPROBE = 'paths.ffprobe_path'
    PATH_PYTHON = 'paths.python_path'
    
    # OCR配置
    OCR_LANG = 'ocr.lang'
    OCR_USE_GPU = 'ocr.use_gpu'
    OCR_ENABLE_MKLDNN = 'ocr.enable_mkldnn'
    OCR_DET_DB_THRESH = 'ocr.det_db_thresh'
    OCR_DET_DB_BOX_THRESH = 'ocr.det_db_box_thresh'
    OCR_REC_SCORE_THRESH = 'ocr.rec_score_thresh'
    OCR_FRAME_INTERVAL = 'ocr.frame_interval'
    OCR_FRAME_QUALITY = 'ocr.frame_quality'
    
    # 字幕配置
    SUBTITLE_MIN_LENGTH = 'subtitle.min_length'
    SUBTITLE_MAX_GAP = 'subtitle.max_gap'
    SUBTITLE_MAX_DURATION = 'subtitle.max_duration'
    SUBTITLE_SIMILARITY_THRESHOLD = 'subtitle.similarity_threshold'
    
    # 翻译配置
    TRANS_FRAMEWORK = 'translation.framework'
    TRANS_HOST = 'translation.host'
    TRANS_MODEL = 'translation.model'
    TRANS_TIMEOUT = 'translation.timeout'
    TRANS_MAX_RETRIES = 'translation.max_retries'
    TRANS_TEMPERATURE = 'translation.temperature'
    
    # ASS样式配置
    ASS_FONT_NAME = 'ass_style.font_name'
    ASS_FONT_SIZE = 'ass_style.font_size'
    ASS_PRIMARY_COLOR = 'ass_style.primary_color'
    ASS_OUTLINE_COLOR = 'ass_style.outline_color'
    ASS_OUTLINE_WIDTH = 'ass_style.outline_width'
    ASS_SHADOW = 'ass_style.shadow'
    ASS_MARGIN_V = 'ass_style.margin_v'
    
    # 烧录配置
    BURN_PRESET = 'burn.preset'
    BURN_CRF = 'burn.crf'
    
    # 处理配置
    PROCESSING_AUTO_SKIP = 'processing.auto_skip_processed'
    PROCESSING_WAIT_BETWEEN = 'processing.wait_between_videos'
    PROCESSING_CLEANUP = 'processing.cleanup_temp'
    PROCESSING_TEMP_DIR = 'processing.temp_dir'
    
    # UI配置
    UI_THEME = 'ui.theme'
    UI_FONT_SIZE = 'ui.font_size'
    UI_LOG_FONT_SIZE = 'ui.log_font_size'
    UI_LOG_MAX_LINES = 'ui.log_max_lines'
    UI_PROGRESS_INTERVAL = 'ui.progress_update_interval'
    UI_WINDOW_WIDTH = 'ui.window_width'
    UI_WINDOW_HEIGHT = 'ui.window_height'


def get_base_dir():
    """获取程序基础目录，兼容PyInstaller打包"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_config_dir():
    """获取配置目录，兼容PyInstaller打包"""
    base_dir = get_base_dir()
    config_dir = os.path.join(base_dir, "config")
    os.makedirs(config_dir, exist_ok=True)
    return config_dir


def get_bin_dir():
    """获取bin目录（存放FFmpeg等工具），兼容PyInstaller打包"""
    base_dir = get_base_dir()
    bin_dir = os.path.join(base_dir, "bin")
    return bin_dir


def get_ffmpeg_path():
    """获取默认的 FFmpeg 路径，优先从 bin 目录查找"""
    base_dir = get_base_dir()
    
    # 检查常规的 bin 目录
    bin_dir = os.path.join(base_dir, "bin")
    ffmpeg_path = os.path.join(bin_dir, "ffmpeg.exe")
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path
    
    # 检查 PyInstaller 打包后的 _internal/bin 目录
    internal_bin_dir = os.path.join(base_dir, "_internal", "bin")
    ffmpeg_path = os.path.join(internal_bin_dir, "ffmpeg.exe")
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path
    
    return "ffmpeg"


def get_ffprobe_path():
    """获取默认的 ffprobe 路径，优先从 bin 目录查找"""
    base_dir = get_base_dir()
    
    # 检查常规的 bin 目录
    bin_dir = os.path.join(base_dir, "bin")
    ffprobe_path = os.path.join(bin_dir, "ffprobe.exe")
    if os.path.exists(ffprobe_path):
        return ffprobe_path
    
    # 检查 PyInstaller 打包后的 _internal/bin 目录
    internal_bin_dir = os.path.join(base_dir, "_internal", "bin")
    ffprobe_path = os.path.join(internal_bin_dir, "ffprobe.exe")
    if os.path.exists(ffprobe_path):
        return ffprobe_path
    
    return "ffprobe"


class ConfigManager:
    """配置管理器类"""

    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "paths": {
            "video_input": "./videos",
            "output_dir": "./output",
            "ffmpeg_path": "ffmpeg",
            "ffprobe_path": "ffprobe",
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
            "cleanup_temp": True,
            "temp_dir": ""
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
                self._validate_and_fix_config()
                logger.info(f"配置文件加载成功: {self.config_file}")
            except Exception as e:
                logger.error(f"加载配置失败: {e}")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            self.config = self.DEFAULT_CONFIG.copy()
        
        self._auto_set_ffmpeg_paths()
        
        if not os.path.exists(self.config_file):
            self.save()
            
        return True
    
    def _validate_and_fix_config(self):
        """验证配置值并修复无效值"""
        validations = [
            (ConfigKeys.OCR_DET_DB_THRESH, lambda x: 0.0 <= x <= 1.0, 0.3),
            (ConfigKeys.OCR_DET_DB_BOX_THRESH, lambda x: 0.0 <= x <= 1.0, 0.5),
            (ConfigKeys.OCR_REC_SCORE_THRESH, lambda x: 0.0 <= x <= 1.0, 0.5),
            (ConfigKeys.OCR_FRAME_INTERVAL, lambda x: x > 0, 1),
            (ConfigKeys.SUBTITLE_MIN_LENGTH, lambda x: x >= 0, 2),
            (ConfigKeys.SUBTITLE_MAX_GAP, lambda x: x > 0, 3.0),
            (ConfigKeys.SUBTITLE_MAX_DURATION, lambda x: x > 0, 30.0),
            (ConfigKeys.SUBTITLE_SIMILARITY_THRESHOLD, lambda x: 0.0 <= x <= 1.0, 0.8),
            (ConfigKeys.TRANS_TIMEOUT, lambda x: x > 0, 120),
            (ConfigKeys.TRANS_MAX_RETRIES, lambda x: x > 0, 3),
            (ConfigKeys.TRANS_TEMPERATURE, lambda x: 0.0 <= x <= 1.0, 0.3),
            (ConfigKeys.BURN_CRF, lambda x: 0 <= x <= 51, 23),
        ]
        
        for key, validator, default in validations:
            value = self.get(key)
            try:
                if not validator(value):
                    logger.warning(f"配置值无效 {key}={value}，已重置为默认值 {default}")
                    self.set(key, default)
            except (TypeError, ValueError):
                logger.warning(f"配置值类型错误 {key}={value}，已重置为默认值 {default}")
                self.set(key, default)

    def _auto_set_ffmpeg_paths(self):
        """自动设置 FFmpeg 路径，优先从 bin 目录查找"""
        base_dir = get_base_dir()
        
        # 处理 ffmpeg_path
        ffmpeg_bin = None
        # 先检查常规的 bin 目录
        bin_dir = os.path.join(base_dir, "bin")
        temp_path = os.path.join(bin_dir, "ffmpeg.exe")
        if os.path.exists(temp_path):
            ffmpeg_bin = temp_path
        else:
            # 再检查 PyInstaller 打包后的 _internal/bin 目录
            internal_bin_dir = os.path.join(base_dir, "_internal", "bin")
            temp_path = os.path.join(internal_bin_dir, "ffmpeg.exe")
            if os.path.exists(temp_path):
                ffmpeg_bin = temp_path
        
        if ffmpeg_bin:
            current_path = self.config.get("paths", {}).get("ffmpeg_path", "")
            if not current_path or current_path == "ffmpeg":
                self.config["paths"]["ffmpeg_path"] = ffmpeg_bin
        
        # 处理 ffprobe_path
        ffprobe_bin = None
        temp_path = os.path.join(bin_dir, "ffprobe.exe")
        if os.path.exists(temp_path):
            ffprobe_bin = temp_path
        else:
            temp_path = os.path.join(internal_bin_dir, "ffprobe.exe")
            if os.path.exists(temp_path):
                ffprobe_bin = temp_path
        
        if ffprobe_bin:
            current_path = self.config.get("paths", {}).get("ffprobe_path", "")
            if not current_path or current_path == "ffprobe":
                self.config["paths"]["ffprobe_path"] = ffprobe_bin

    def save(self) -> bool:
        """保存配置文件"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info(f"配置文件已保存: {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    def reload(self) -> bool:
        """热重载配置文件"""
        old_config = self.config.copy()
        success = self.load()
        
        if success:
            changed_keys = []
            for key in ['ocr', 'translation', 'ass_style', 'burn']:
                if old_config.get(key) != self.config.get(key):
                    changed_keys.append(key)
            
            if changed_keys:
                logger.info(f"配置已热重载，以下模块配置已更新: {', '.join(changed_keys)}")
        
        return success

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
        self._auto_set_ffmpeg_paths()
        return self.save()


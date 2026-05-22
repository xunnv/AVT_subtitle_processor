"""
日志系统模块
集成 Python logging 模块，支持文件持久化和级别配置
"""

import logging
import os
from datetime import datetime
from typing import Optional
from logging.handlers import TimedRotatingFileHandler


class Logger:
    """增强日志系统"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, log_dir: Optional[str] = None, level: str = "INFO"):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._initialized = True
        self.log_dir = log_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.level = level
        self._log_viewer = None
        
        self._setup_logger()
    
    def _setup_logger(self):
        """配置日志记录器"""
        self.logger = logging.getLogger("AVT")
        self.logger.setLevel(getattr(logging, self.level))
        
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler = TimedRotatingFileHandler(
            os.path.join(self.log_dir, "avt.log"),
            when='midnight',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, self.level))
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def set_log_viewer(self, log_viewer):
        """设置日志查看器回调"""
        self._log_viewer = log_viewer
    
    def _notify_viewer(self, message: str, level: str):
        """通知日志查看器"""
        if self._log_viewer:
            level_map = {
                'DEBUG': 'info',
                'INFO': 'info',
                'WARNING': 'warning',
                'ERROR': 'error',
                'CRITICAL': 'error'
            }
            self._log_viewer.log(message, level_map.get(level, 'info'))
    
    def debug(self, message: str, *args, **kwargs):
        """调试日志"""
        self.logger.debug(message, *args, **kwargs)
        self._notify_viewer(message, 'DEBUG')
    
    def info(self, message: str, *args, **kwargs):
        """信息日志"""
        self.logger.info(message, *args, **kwargs)
        self._notify_viewer(message, 'INFO')
    
    def warning(self, message: str, *args, **kwargs):
        """警告日志"""
        self.logger.warning(message, *args, **kwargs)
        self._notify_viewer(message, 'WARNING')
    
    def error(self, message: str, *args, **kwargs):
        """错误日志"""
        self.logger.error(message, *args, **kwargs)
        self._notify_viewer(message, 'ERROR')
    
    def critical(self, message: str, *args, **kwargs):
        """严重错误日志"""
        self.logger.critical(message, *args, **kwargs)
        self._notify_viewer(message, 'CRITICAL')
    
    def exception(self, message: str, *args, exc_info=True, **kwargs):
        """异常日志（自动包含堆栈信息）"""
        self.logger.exception(message, *args, exc_info=exc_info, **kwargs)
        self._notify_viewer(message, 'ERROR')
    
    def set_level(self, level: str):
        """设置日志级别"""
        self.level = level
        self.logger.setLevel(getattr(logging, level))
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(getattr(logging, level))
    
    def get_log_file_path(self) -> str:
        """获取当前日志文件路径"""
        for handler in self.logger.handlers:
            if isinstance(handler, TimedRotatingFileHandler):
                return handler.baseFilename
        return ""
    
    def get_recent_logs(self, lines: int = 100) -> str:
        """获取最近的日志内容"""
        log_path = self.get_log_file_path()
        if not log_path or not os.path.exists(log_path):
            return ""
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
                return ''.join(log_lines[-lines:])
        except Exception:
            return ""


logger = Logger()
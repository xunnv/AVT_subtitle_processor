"""
安全工具模块
提供路径安全校验和输入验证功能
"""

import os
import re
from typing import Optional, Tuple
from .logger import logger


class PathSecurity:
    """路径安全校验工具"""
    
    @staticmethod
    def validate_path(file_path: str, allowed_base_dirs: Optional[list] = None) -> Tuple[bool, str]:
        """
        验证文件路径的安全性
        
        Args:
            file_path: 待验证的文件路径
            allowed_base_dirs: 允许的基础目录列表（可选）
        
        Returns:
            (是否安全, 错误信息)
        """
        if not file_path or not isinstance(file_path, str):
            return False, "路径不能为空"
        
        try:
            abs_path = os.path.abspath(file_path)
        except Exception:
            return False, "无效的路径格式"
        
        if '..' in file_path or '..' in abs_path:
            logger.warning(f"检测到路径遍历尝试: {file_path}")
            return False, "路径包含非法字符（路径遍历攻击）"
        
        if allowed_base_dirs:
            allowed = False
            for base_dir in allowed_base_dirs:
                base_abs = os.path.abspath(base_dir)
                if abs_path.startswith(base_abs):
                    allowed = True
                    break
            
            if not allowed:
                logger.warning(f"路径不在允许的目录范围内: {file_path}")
                return False, "路径不在允许的目录范围内"
        
        return True, ""
    
    @staticmethod
    def validate_file_exists(file_path: str) -> Tuple[bool, str]:
        """
        验证文件是否存在
        
        Args:
            file_path: 待验证的文件路径
        
        Returns:
            (是否存在, 错误信息)
        """
        if not os.path.exists(file_path):
            return False, f"文件不存在: {file_path}"
        
        if not os.path.isfile(file_path):
            return False, f"不是有效的文件: {file_path}"
        
        return True, ""
    
    @staticmethod
    def validate_directory_exists(dir_path: str) -> Tuple[bool, str]:
        """
        验证目录是否存在
        
        Args:
            dir_path: 待验证的目录路径
        
        Returns:
            (是否存在, 错误信息)
        """
        if not os.path.exists(dir_path):
            return False, f"目录不存在: {dir_path}"
        
        if not os.path.isdir(dir_path):
            return False, f"不是有效的目录: {dir_path}"
        
        return True, ""
    
    @staticmethod
    def validate_video_file(file_path: str) -> Tuple[bool, str]:
        """
        验证视频文件的安全性和有效性
        
        Args:
            file_path: 待验证的视频文件路径
        
        Returns:
            (是否有效, 错误信息)
        """
        valid, msg = PathSecurity.validate_path(file_path)
        if not valid:
            return False, msg
        
        valid, msg = PathSecurity.validate_file_exists(file_path)
        if not valid:
            return False, msg
        
        allowed_extensions = ('.mp4', '.mkv', '.mov', '.avi', '.m4v', '.webm', '.flv')
        _, ext = os.path.splitext(file_path.lower())
        if ext not in allowed_extensions:
            return False, f"不支持的视频格式: {ext}，支持的格式: {allowed_extensions}"
        
        return True, ""
    
    @staticmethod
    def validate_output_path(output_path: str) -> Tuple[bool, str]:
        """
        验证输出路径的安全性
        
        Args:
            output_path: 待验证的输出路径
        
        Returns:
            (是否有效, 错误信息)
        """
        if not output_path or not isinstance(output_path, str):
            return False, "输出路径不能为空"
        
        try:
            abs_path = os.path.abspath(output_path)
        except Exception:
            return False, "无效的路径格式"
        
        if '..' in output_path or '..' in abs_path:
            return False, "路径包含非法字符"
        
        return True, ""


class InputValidator:
    """输入验证工具"""
    
    @staticmethod
    def validate_string(input_str: str, min_length: int = 0, max_length: int = 1000) -> Tuple[bool, str]:
        """
        验证字符串输入
        
        Args:
            input_str: 待验证的字符串
            min_length: 最小长度（默认0）
            max_length: 最大长度（默认1000）
        
        Returns:
            (是否有效, 错误信息)
        """
        if not isinstance(input_str, str):
            return False, "输入必须是字符串"
        
        if len(input_str) < min_length:
            return False, f"输入长度不足，最少需要 {min_length} 个字符"
        
        if len(input_str) > max_length:
            return False, f"输入长度过长，最多允许 {max_length} 个字符"
        
        return True, ""
    
    @staticmethod
    def validate_positive_integer(value, min_value: int = 1, max_value: int = 1000000) -> Tuple[bool, str]:
        """
        验证正整数
        
        Args:
            value: 待验证的值
            min_value: 最小值（默认1）
            max_value: 最大值（默认1000000）
        
        Returns:
            (是否有效, 错误信息)
        """
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            return False, "必须是整数"
        
        if int_value < min_value:
            return False, f"值必须大于等于 {min_value}"
        
        if int_value > max_value:
            return False, f"值必须小于等于 {max_value}"
        
        return True, ""
    
    @staticmethod
    def validate_float(value, min_value: float = 0.0, max_value: float = 1.0) -> Tuple[bool, str]:
        """
        验证浮点数
        
        Args:
            value: 待验证的值
            min_value: 最小值（默认0.0）
            max_value: 最大值（默认1.0）
        
        Returns:
            (是否有效, 错误信息)
        """
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            return False, "必须是数字"
        
        if float_value < min_value:
            return False, f"值必须大于等于 {min_value}"
        
        if float_value > max_value:
            return False, f"值必须小于等于 {max_value}"
        
        return True, ""
    
    @staticmethod
    def validate_boolean(value) -> Tuple[bool, str]:
        """
        验证布尔值
        
        Args:
            value: 待验证的值
        
        Returns:
            (是否有效, 错误信息)
        """
        if isinstance(value, bool):
            return True, ""
        
        if value in ('true', 'True', '1', 'yes', 'on'):
            return True, ""
        
        if value in ('false', 'False', '0', 'no', 'off'):
            return True, ""
        
        return False, "必须是布尔值"

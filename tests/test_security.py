"""
安全工具单元测试
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.security import PathSecurity, InputValidator


class TestPathSecurity:
    """路径安全测试类"""
    
    def test_validate_path_normal(self):
        """测试正常路径"""
        valid, msg = PathSecurity.validate_path("/valid/path/file.txt")
        assert valid == True
        assert msg == ""
    
    def test_validate_path_traversal(self):
        """测试路径遍历攻击"""
        valid, msg = PathSecurity.validate_path("/valid/path/../../etc/passwd")
        assert valid == False
        assert "路径遍历" in msg
    
    def test_validate_path_empty(self):
        """测试空路径"""
        valid, msg = PathSecurity.validate_path("")
        assert valid == False
        assert "不能为空" in msg
    
    def test_validate_path_allowed_dirs(self):
        """测试允许的目录范围"""
        allowed_dirs = ["/home/user"]
        valid, msg = PathSecurity.validate_path("/home/user/documents/file.txt", allowed_dirs)
        assert valid == True
        
        valid, msg = PathSecurity.validate_path("/etc/passwd", allowed_dirs)
        assert valid == False
        assert "不在允许的目录范围内" in msg
    
    def test_validate_video_file(self):
        """测试视频文件验证"""
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            f.write(b"test video content")
            temp_path = f.name
        
        try:
            valid, msg = PathSecurity.validate_video_file(temp_path)
            assert valid == True
        finally:
            os.unlink(temp_path)
    
    def test_validate_video_file_invalid_ext(self):
        """测试无效视频格式"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test content")
            temp_path = f.name
        
        try:
            valid, msg = PathSecurity.validate_video_file(temp_path)
            assert valid == False
            assert "不支持的视频格式" in msg
        finally:
            os.unlink(temp_path)


class TestInputValidator:
    """输入验证测试类"""
    
    def test_validate_string(self):
        """测试字符串验证"""
        valid, msg = InputValidator.validate_string("test", min_length=2, max_length=10)
        assert valid == True
        
        valid, msg = InputValidator.validate_string("a", min_length=2)
        assert valid == False
        assert "长度不足" in msg
    
    def test_validate_positive_integer(self):
        """测试正整数验证"""
        valid, msg = InputValidator.validate_positive_integer(10, min_value=1, max_value=100)
        assert valid == True
        
        valid, msg = InputValidator.validate_positive_integer(0)
        assert valid == False
        assert "必须大于等于" in msg
    
    def test_validate_float(self):
        """测试浮点数验证"""
        valid, msg = InputValidator.validate_float(0.5)
        assert valid == True
        
        valid, msg = InputValidator.validate_float(1.5)
        assert valid == False
        assert "必须小于等于" in msg
    
    def test_validate_boolean(self):
        """测试布尔值验证"""
        valid, msg = InputValidator.validate_boolean(True)
        assert valid == True
        
        valid, msg = InputValidator.validate_boolean("true")
        assert valid == True
        
        valid, msg = InputValidator.validate_boolean("invalid")
        assert valid == False


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
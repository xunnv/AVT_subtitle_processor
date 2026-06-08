"""
配置管理器单元测试
"""

import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.config_manager import ConfigManager, ConfigKeys


class TestConfigManager:
    """配置管理器测试类"""

    def setup_method(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.temp_dir)

    def teardown_method(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)

    def test_default_config(self):
        """测试默认配置加载"""
        assert self.config_manager.get(ConfigKeys.OCR_LANG) == "japan"
        assert self.config_manager.get(ConfigKeys.OCR_USE_GPU) == True
        assert self.config_manager.get(ConfigKeys.TRANS_FRAMEWORK) == "ollama"

    def test_get_set_config(self):
        """测试配置读写"""
        self.config_manager.set(ConfigKeys.OCR_LANG, "chinese")
        assert self.config_manager.get(ConfigKeys.OCR_LANG) == "chinese"

        self.config_manager.set(ConfigKeys.OCR_FRAME_INTERVAL, 2)
        assert self.config_manager.get(ConfigKeys.OCR_FRAME_INTERVAL) == 2

    def test_config_validation(self):
        """测试配置验证"""
        self.config_manager.set(ConfigKeys.OCR_DET_DB_THRESH, 1.5)
        self.config_manager._validate_and_fix_config()
        assert self.config_manager.get(ConfigKeys.OCR_DET_DB_THRESH) == 0.3

        self.config_manager.set(ConfigKeys.BURN_CRF, 100)
        self.config_manager._validate_and_fix_config()
        assert self.config_manager.get(ConfigKeys.BURN_CRF) == 23

    def test_save_reload(self):
        """测试配置保存和重载"""
        self.config_manager.set(ConfigKeys.OCR_LANG, "english")
        self.config_manager.save()

        new_manager = ConfigManager(self.temp_dir)
        assert new_manager.get(ConfigKeys.OCR_LANG) == "english"

    def test_get_translation_config(self):
        """测试获取翻译配置"""
        config = self.config_manager.get_translation_config()
        assert 'framework' in config
        assert 'host' in config
        assert 'model' in config


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

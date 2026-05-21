import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing basic imports...")

try:
    import ctypes
    print("ctypes imported successfully")
except Exception as e:
    print(f"Failed to import ctypes: {e}")

try:
    from PyQt5.QtWidgets import QApplication
    print("PyQt5 imported successfully")
except Exception as e:
    print(f"Failed to import PyQt5: {e}")

try:
    from modules.config_manager import ConfigManager, get_bin_dir
    print("ConfigManager imported successfully")
    
    bin_dir = get_bin_dir()
    print(f"bin_dir: {bin_dir}")
    print(f"bin_dir exists: {os.path.exists(bin_dir)}")
    
    config = ConfigManager()
    print(f"Config loaded successfully")
    print(f"FFmpeg path: {config.get('paths.ffmpeg_path')}")
    print(f"FFmpeg exists: {os.path.exists(config.get('paths.ffmpeg_path'))}")
except Exception as e:
    print(f"Failed to import ConfigManager: {e}")

print("\nTest completed!")
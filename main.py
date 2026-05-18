"""
AVT字幕处理器 - 主程序入口
"""

import sys
import os
import traceback
import ctypes

# 在导入 PyQt5 之前隐藏控制台窗口（仅 Windows）
if sys.platform == 'win32':
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32
    hWnd = kernel32.GetConsoleWindow()
    if hWnd:
        user32.ShowWindow(hWnd, 0)

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.config_manager import ConfigManager
from modules.video_manager import VideoManager
from modules.subtitle_engine import SubtitleEngine
from modules.main_window import MainWindow


def get_config_dir():
    """获取配置目录，兼容PyInstaller打包"""
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), "config")
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")


class AVTApplication:
    """AVT应用程序类"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("AVT字幕处理器")
        self.app.setApplicationVersion("1.0.0")
        self.app.setStyle('Fusion')

        self._setup_application()

        config_dir = get_config_dir()
        self.config_manager = ConfigManager(config_dir)
        self.video_manager = VideoManager(self.config_manager)
        self.engine = SubtitleEngine(self.config_manager)

        ui_font_size = 27
        font = QFont("Microsoft YaHei", ui_font_size)
        font.setPointSizeF(ui_font_size)
        self.app.setFont(font)

        self.main_window = MainWindow()
        self.main_window.setup_components(
            self.config_manager,
            self.video_manager,
            self.engine
        )

    def _setup_application(self):
        """设置应用程序"""
        self.app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        self.app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    def run(self):
        """运行应用程序"""
        try:
            self.main_window.show()
            return self.app.exec_()
        except Exception as e:
            error_msg = f"程序发生错误:\n{str(e)}\n\n{traceback.format_exc()}"
            print(error_msg)
            QMessageBox.critical(None, "错误", error_msg)
            return 1


def except_hook(exc_type, exc_value, exc_traceback):
    """全局异常处理器"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_msg = f"{exc_type.__name__}: {exc_value}\n\n{''.join(traceback.format_tb(exc_traceback))}"
    print(error_msg)

    try:
        QMessageBox.critical(None, "未捕获的异常", error_msg)
    except:
        pass

    sys.exit(1)


def main():
    """主函数"""
    sys.excepthook = except_hook

    app = AVTApplication()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())

"""
AVT字幕处理器 - 主程序入口
"""

import sys
import os
import traceback
import ctypes


def setup_nvidia_path():
    """设置 NVIDIA CUDA 运行时库的路径（兼容PyInstaller打包）"""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        nvidia_base = os.path.join(base_dir, '_internal', 'nvidia')

        nvidia_bins = [
            os.path.join(nvidia_base, 'cublas', 'bin'),
            os.path.join(nvidia_base, 'cuda_runtime', 'bin'),
            os.path.join(nvidia_base, 'cudnn', 'bin'),
            os.path.join(nvidia_base, 'cufft', 'bin'),
            os.path.join(nvidia_base, 'curand', 'bin'),
            os.path.join(nvidia_base, 'cusolver', 'bin'),
            os.path.join(nvidia_base, 'cusparse', 'bin'),
            os.path.join(nvidia_base, 'nvjitlink', 'bin'),
        ]

        current_path = os.environ.get('PATH', '')
        paths_to_add = []

        for bin_path in nvidia_bins:
            if os.path.exists(bin_path) and bin_path not in current_path:
                paths_to_add.append(bin_path)

        if paths_to_add:
            new_path = ';'.join(paths_to_add) + ';' + current_path
            os.environ['PATH'] = new_path


def check_vc_redist():
    """检查 Microsoft Visual C++ Redistributable 是否安装"""
    if sys.platform != 'win32':
        return True

    # 检查 VC++ 2015-2022 Redistributable (x64)
    required_dlls = [
        'vcruntime140.dll',
        'vcruntime140_1.dll',
        'msvcp140.dll',
        'msvcp140_1.dll',
        'msvcp140_2.dll',
    ]

    missing_dlls = []
    for dll in required_dlls:
        try:
            ctypes.CDLL(dll)
        except OSError:
            missing_dlls.append(dll)

    if missing_dlls:
        return False, missing_dlls
    return True, None


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
        # 首先检查 VC++ 运行时
        self._check_vc_redist()

        self.app = QApplication(sys.argv)
        self.app.setApplicationName("AVT字幕处理器")
        self.app.setApplicationVersion("1.0.0")
        self.app.setStyle('Fusion')

        self._setup_application()

        config_dir = get_config_dir()
        self.config_manager = ConfigManager(config_dir)
        self.video_manager = VideoManager(self.config_manager)
        self.engine = SubtitleEngine(self.config_manager)

        # 设置UI字体
        self._setup_ui_font()

        # 创建主窗口
        self._create_main_window()

    def _check_vc_redist(self):
        """检查 VC++ 运行时库"""
        installed, missing = check_vc_redist()
        if not installed:
            error_msg = (
                "缺少必要的运行时库！\n\n"
                "请先安装 Microsoft Visual C++ 2015-2022 Redistributable (x64)\n\n"
                f"缺少的文件: {', '.join(missing)}\n\n"
                "下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe"
            )
            print(error_msg)

            # 尝试显示错误消息框（即使还没初始化完整）
            try:
                temp_app = QApplication(sys.argv)
                QMessageBox.critical(None, "运行时错误", error_msg)
            except:
                pass

            sys.exit(1)

    def _setup_ui_font(self):
        """设置UI字体"""
        ui_font_size = 27
        font = QFont("Microsoft YaHei", ui_font_size)
        font.setPointSizeF(ui_font_size)
        self.app.setFont(font)

    def _create_main_window(self):
        """创建主窗口"""
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

    # 设置 NVIDIA CUDA 运行时库路径（必须在导入 paddle 之前调用）
    setup_nvidia_path()

    app = AVTApplication()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())

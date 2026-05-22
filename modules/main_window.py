"""
主窗口模块
AVT字幕处理器的主界面
"""

import os
import time
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QPushButton, QLineEdit, QComboBox,
                             QSpinBox, QLabel, QGroupBox, QFormLayout,
                             QTableWidget, QTableWidgetItem, QProgressBar,
                             QStatusBar, QMessageBox, QFileDialog, QScrollArea,
                             QAction, QMenuBar, QToolBar, QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont

from modules.log_viewer import LogViewer
from modules.config_manager import ConfigManager
from modules.video_manager import VideoStatus


class ModernStyle:
    """现代化暗色系主题样式"""

    @staticmethod
    def get_stylesheet(font_size: int = 27) -> str:
        """生成暗色主题样式表"""
        stylesheet = """
            QMainWindow {
                background: #1a1a2e;
            }
            QWidget {
                font-family: "Microsoft YaHei", "Segoe UI", Arial;
                font-size: __FONT_SIZE__px;
                color: #e0e0e0;
            }
            QMenuBar {
                background: #252536;
                color: #e0e0e0;
                border: none;
                padding: 5px;
            }
            QMenuBar::item {
                background: transparent;
                color: #e0e0e0;
                padding: 7px 14px;
                border-radius: 4px;
                font-size: __FONT_SIZE__px;
            }
            QMenuBar::item:selected {
                background: #3d3d5c;
            }
            QMenu {
                background: #252536;
                border: 1px solid #3d3d5c;
                border-radius: 8px;
                padding: 4px;
                color: #e0e0e0;
            }
            QMenu::item {
                padding: 8px 35px;
                border-radius: 4px;
                font-size: __FONT_SIZE__px;
                color: #e0e0e0;
            }
            QMenu::item:selected {
                background: #3d3d5c;
            }
            QToolBar {
                background: #252536;
                border: none;
                border-bottom: 1px solid #3d3d5c;
                padding: 6px 12px;
                spacing: 10px;
            }
            QGroupBox {
                font-weight: bold;
                font-size: __FONT_SIZE__px;
                color: #7c6fdc;
                border: 1.5px solid #3d3d5c;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 12px;
                background: #252536;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #9d8fdf;
            }
            QLabel {
                color: #c0c0c0;
                font-size: __FONT_SIZE__px;
            }
            QFormLayout > QLabel {
                font-size: __FONT_SIZE__px;
                color: #a0a0a0;
                min-width: 80px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d3d5c, stop:1 #2d2d4a);
                color: #e0e0e0;
                border: 1px solid #4d4d6c;
                border-radius: 6px;
                padding: 8px 18px;
                font-weight: bold;
                font-size: __FONT_SIZE__px;
                min-width: 75px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4d4d6c, stop:1 #3d3d5a);
                border-color: #6d6d8c;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d4a, stop:1 #1d1d3a);
            }
            QPushButton:disabled {
                background: #2a2a3a;
                color: #606070;
                border-color: #3a3a4a;
            }
            QPushButton#btn_start {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d4a3d, stop:1 #1d3a2d);
                color: #7dcea0;
                border: 1px solid #3d6a4d;
            }
            QPushButton#btn_start:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d5a4d, stop:1 #2d4a3d);
            }
            QPushButton#btn_stop {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a2d3d, stop:1 #3a1d2d);
                color: #e07d7d;
                border: 1px solid #6a3d4d;
            }
            QPushButton#btn_stop:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a3d4d, stop:1 #4a2d3d);
            }
            QLineEdit, QSpinBox, QDoubleSpinBox {
                padding: 8px 12px;
                border: 1.5px solid #3d3d5c;
                border-radius: 6px;
                background: #1a1a2e;
                color: #e0e0e0;
                font-size: __FONT_SIZE__px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #7c6fdc;
                background: #1e1e32;
            }
            QLineEdit::placeholder {
                color: #606070;
            }
            QComboBox {
                padding: 8px 12px;
                border: 1.5px solid #3d3d5c;
                border-radius: 6px;
                background: #1a1a2e;
                color: #e0e0e0;
                font-size: __FONT_SIZE__px;
            }
            QComboBox:focus {
                border-color: #7c6fdc;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #7c6fdc;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background: #252536;
                border: 1px solid #3d3d5c;
                border-radius: 6px;
                selection-background-color: #3d3d5c;
                padding: 4px;
                font-size: __FONT_SIZE__px;
                color: #e0e0e0;
            }
            QCheckBox {
                spacing: 8px;
                color: #c0c0c0;
                font-size: __FONT_SIZE__px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1.5px solid #4d4d6c;
                background: #1a1a2e;
            }
            QCheckBox::indicator:checked {
                background: #7c6fdc;
                border-color: #9d8fdf;
            }
            QCheckBox::indicator:hover {
                border-color: #7c6fdc;
            }
            QTableWidget {
                background: #1a1a2e;
                border: none;
                border-radius: 10px;
                gridline-color: #3d3d5c;
                selection-background-color: #3d3d5c;
                selection-color: #e0e0e0;
                outline: none;
                font-size: __FONT_SIZE__px;
                color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 10px 6px;
                border-bottom: 1px solid #2d2d4c;
                color: #e0e0e0;
                background: transparent;
            }
            QTableWidget::item:selected {
                background: #3d3d5c;
                color: #ffffff;
            }
            QTableWidget::item:hover {
                background: #2d2d4a;
            }
            QTableWidget::item:selected:!active {
                background: #3d3d5c;
                color: #ffffff;
            }
            QTableWidget QTableCornerButton::section {
                background: #252536;
                border: none;
                border-bottom: 1px solid #3d3d5c;
                border-right: 1px solid #3d3d5c;
            }
            QHeaderView::section {
                background: #252536;
                color: #c0c0c0;
                padding: 12px;
                border: none;
                border-bottom: 1px solid #3d3d5c;
                font-weight: bold;
                font-size: __FONT_SIZE__px;
            }
            QHeaderView::section:horizontal {
                background: #252536;
            }
            QHeaderView::section:vertical {
                background: #252536;
                color: #c0c0c0;
                padding: 6px;
                border-right: 1px solid #3d3d5c;
            }
            QHeaderView {
                background: #252536;
                border: none;
            }
            QProgressBar {
                height: 22px;
                border-radius: 11px;
                background: #2d2d4a;
                text-align: center;
                font-weight: bold;
                font-size: __FONT_SIZE__px;
                color: #ffffff;
                border: none;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6c5fdc, stop:1 #7c6fdc);
                border-radius: 11px;
            }
            QTabWidget::pane {
                border: none;
                background: #252536;
                border-radius: 10px;
            }
            QTabBar::tab {
                background: #1a1a2e;
                color: #a0a0a0;
                padding: 12px 24px;
                margin-right: 3px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: __FONT_SIZE__px;
            }
            QTabBar::tab:selected {
                background: #252536;
                color: #7c6fdc;
            }
            QTabBar::tab:hover:!selected {
                background: #2d2d4a;
                color: #c0c0c0;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 9px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #3d3d5c;
                border-radius: 4px;
                min-height: 35px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4d4d6c;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background: transparent;
                height: 9px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background: #3d3d5c;
                border-radius: 4px;
                min-width: 35px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #4d4d6c;
            }
            QStatusBar {
                background: #252536;
                color: #a0a0a0;
                padding: 6px 12px;
                font-size: __FONT_SIZE__px;
                border-top: 1px solid #3d3d5c;
            }
            QTextEdit {
                background: #1a1a2e;
                color: #e0e0e0;
                border: 1px solid #3d3d5c;
                border-radius: 6px;
                padding: 8px;
            }
            QListWidget {
                background: #1a1a2e;
                color: #e0e0e0;
                border: 1px solid #3d3d5c;
                border-radius: 6px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2d2d4a;
            }
            QListWidget::item:selected {
                background: #3d3d5c;
                color: #ffffff;
            }
            QSplitter::handle {
                background: #3d3d5c;
            }
            QSplitter::handle:horizontal {
                width: 2px;
            }
            QSplitter::handle:vertical {
                height: 2px;
            }
            QScrollArea {
                background: #252536;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: #252536;
            }
            QScrollArea > QWidget {
                background: #252536;
            }
            QMessageBox {
                background: #1a1a2e;
                border: 1px solid #3d3d5c;
                border-radius: 10px;
            }
            QMessageBox QLabel {
                color: #e0e0e0;
                font-size: __FONT_SIZE__px;
            }
            QMessageBox QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d3d5c, stop:1 #2d2d4a);
                color: #e0e0e0;
                border: 1px solid #4d4d6c;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: __FONT_SIZE__px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4d4d6c, stop:1 #3d3d5a);
                border-color: #6d6d8c;
            }
            QMessageBox QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d2d4a, stop:1 #1d1d3a);
            }
        """
        return stylesheet.replace("__FONT_SIZE__", str(font_size))


class ProcessingThread(QThread):
    """处理线程"""
    progress_updated = pyqtSignal(int, int, float, str, str)
    finished = pyqtSignal(bool, str)
    cancel_requested_flag = False

    def __init__(self, engine, video_info):
        super().__init__()
        self.engine = engine
        self.video_info = video_info

    def run(self):
        """执行处理"""
        try:
            self.cancel_requested_flag = False

            def progress_callback(step, total, progress, message, eta=""):
                if self.cancel_requested_flag:
                    raise InterruptedError("用户取消")
                self.progress_updated.emit(step, total, progress, message, eta)

            self.engine.set_progress_callback(progress_callback)
            self.engine.cancel_requested = False
            result = self.engine.process_video(self.video_info.path)

            if result.success:
                self.finished.emit(True, result.message)
            else:
                self.finished.emit(False, result.message)

        except InterruptedError:
            self.finished.emit(False, "用户取消")
        except Exception as e:
            self.finished.emit(False, str(e))

    def request_cancel(self):
        """请求取消"""
        self.cancel_requested_flag = True
        if self.engine:
            self.engine.request_cancel()


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AVT字幕处理器")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        self.config_manager = None
        self.video_manager = None
        self.engine = None
        self.timer = None
        self.progress_panel = None
        self.video_list = None
        self.log_viewer = None
        self.status_bar = None
        self.overall_progress = None

        self.edit_input_path = None
        self.edit_output_path = None
        self.combo_framework = None
        self.stacked_translation = None
        self.edit_ollama_host = None
        self.edit_ollama_model = None
        self.spin_ollama_timeout = None
        self.spin_ollama_temp = None
        self.edit_lmstudio_host = None
        self.edit_lmstudio_model = None
        self.spin_lmstudio_timeout = None
        self.spin_lmstudio_temp = None
        self.combo_font_name = None
        self.spin_subtitle_size = None
        self.spin_outline_width = None
        self.spin_margin_v = None

        self.processing_thread = None
        self.current_video_index = 0
        
        self._last_progress_update = 0
        self._progress_update_interval = 0.2
        self._pending_progress = None
        self._progress_timer = None
        
        self._pending_logs = []
        self._last_log_update = 0
        self._log_update_interval = 0.5
        self._log_timer = None

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setStyleSheet(ModernStyle.get_stylesheet(27))
        
        self.resize(950, 1200)
        self.setMinimumSize(800, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self._create_menu_bar()
        self._create_tool_bar()

        self._create_status_bar()

        self.right_panel = self._create_right_panel()
        main_layout.addWidget(self.right_panel, 1)

    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        file_menu = menubar.addMenu("文件")
        refresh_action = QAction("刷新视频列表", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_video_list)
        file_menu.addAction(refresh_action)
        file_menu.addSeparator()
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        config_menu = menubar.addMenu("配置")
        reset_action = QAction("重置配置", self)
        reset_action.triggered.connect(self._reset_config)
        config_menu.addAction(reset_action)

        help_menu = menubar.addMenu("帮助")
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        btn_add = QPushButton("添加视频")
        btn_add.clicked.connect(self._add_video)
        toolbar.addWidget(btn_add)

        btn_remove = QPushButton("移除选中")
        btn_remove.clicked.connect(self._remove_selected)
        toolbar.addWidget(btn_remove)

        toolbar.addSeparator()

        self.btn_start = QPushButton("开始处理")
        self.btn_start.setObjectName("btn_start")
        self.btn_start.clicked.connect(self._start_processing)
        toolbar.addWidget(self.btn_start)

        self.btn_stop = QPushButton("停止")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_processing)
        toolbar.addWidget(self.btn_stop)

        toolbar.addSeparator()

        btn_clear_log = QPushButton("清空日志")
        btn_clear_log.clicked.connect(self._clear_log)
        toolbar.addWidget(btn_clear_log)

    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

    def _create_right_panel(self):
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        tab_widget = QTabWidget()

        progress_tab = self._create_progress_tab()
        tab_widget.addTab(progress_tab, "进度")

        config_tab = self._create_config_tab()
        tab_widget.addTab(config_tab, "配置")

        log_tab = self._create_log_tab()
        tab_widget.addTab(log_tab, "日志")

        layout.addWidget(tab_widget)

        return panel

    def _create_log_tab(self):
        """创建日志选项卡"""
        self.log_viewer = LogViewer()
        return self.log_viewer

    def _create_config_tab(self):
        """创建配置选项卡"""
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        path_group = QGroupBox("路径配置")
        path_layout = QVBoxLayout(path_group)
        path_layout.setSpacing(10)

        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("输入:"))
        self.edit_input_path = QLineEdit()
        self.edit_input_path.setPlaceholderText("选择视频输入目录...")
        input_row.addWidget(self.edit_input_path)
        btn_input = QPushButton("浏览")
        btn_input.setObjectName("btn_browse")
        btn_input.clicked.connect(self._browse_input_path)
        input_row.addWidget(btn_input)
        path_layout.addLayout(input_row)

        output_row = QHBoxLayout()
        output_row.addWidget(QLabel("输出:"))
        self.edit_output_path = QLineEdit()
        self.edit_output_path.setPlaceholderText("选择输出目录...")
        output_row.addWidget(self.edit_output_path)
        btn_output = QPushButton("浏览")
        btn_output.setObjectName("btn_browse")
        btn_output.clicked.connect(self._browse_output_path)
        output_row.addWidget(btn_output)
        path_layout.addLayout(output_row)

        layout.addWidget(path_group)

        ass_style_group = QGroupBox("字幕样式")
        ass_style_layout = QFormLayout(ass_style_group)
        ass_style_layout.setSpacing(10)
        ass_style_layout.setLabelAlignment(Qt.AlignLeft)

        self.combo_font_name = QComboBox()
        self.combo_font_name.addItems([
            "Microsoft YaHei",
            "SimHei",
            "SimSun",
            "Arial",
            "Noto Sans SC",
            "Source Han Sans",
            "PingFang SC"
        ])
        ass_style_layout.addRow("字体:", self.combo_font_name)

        self.spin_subtitle_size = QSpinBox()
        self.spin_subtitle_size.setRange(10, 60)
        self.spin_subtitle_size.setValue(20)
        self.spin_subtitle_size.setSuffix(" px")
        ass_style_layout.addRow("字幕大小:", self.spin_subtitle_size)

        self.spin_outline_width = QSpinBox()
        self.spin_outline_width.setRange(0, 10)
        self.spin_outline_width.setValue(2)
        ass_style_layout.addRow("描边宽度:", self.spin_outline_width)

        self.spin_margin_v = QSpinBox()
        self.spin_margin_v.setRange(10, 200)
        self.spin_margin_v.setValue(30)
        self.spin_margin_v.setSuffix(" px")
        ass_style_layout.addRow("底部边距:", self.spin_margin_v)

        self.combo_font_name.currentIndexChanged.connect(self._on_ass_style_changed)
        self.spin_subtitle_size.valueChanged.connect(self._on_ass_style_changed)
        self.spin_outline_width.valueChanged.connect(self._on_ass_style_changed)
        self.spin_margin_v.valueChanged.connect(self._on_ass_style_changed)

        layout.addWidget(ass_style_group)

        trans_group = QGroupBox("翻译配置")
        trans_layout = QVBoxLayout(trans_group)
        trans_layout.setSpacing(20)
        trans_layout.setContentsMargins(20, 22, 20, 20)

        framework_row = QHBoxLayout()
        framework_row.addWidget(QLabel("框架:"))
        self.combo_framework = QComboBox()
        self.combo_framework.addItems(["Ollama", "LM Studio"])
        self.combo_framework.setMinimumWidth(180)
        self.combo_framework.currentIndexChanged.connect(self._on_framework_changed)
        framework_row.addWidget(self.combo_framework)

        btn_test = QPushButton("测试连接")
        btn_test.clicked.connect(self._test_translation_connection)
        framework_row.addWidget(btn_test)
        framework_row.addStretch()
        trans_layout.addLayout(framework_row)

        self.stacked_translation = QTabWidget()
        self.stacked_translation.setMinimumHeight(380)
        self.stacked_translation.setMinimumWidth(650)

        self.ollama_widget = self._create_ollama_panel()
        self.lmstudio_widget = self._create_lmstudio_panel()

        self.stacked_translation.addTab(self.ollama_widget, "Ollama")
        self.stacked_translation.addTab(self.lmstudio_widget, "LM Studio")

        trans_layout.addWidget(self.stacked_translation)
        layout.addWidget(trans_group)

        layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        return container

    def _create_ollama_panel(self):
        """创建 Ollama 配置面板"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setLabelAlignment(Qt.AlignLeft)

        self.edit_ollama_host = QLineEdit()
        self.edit_ollama_host.setText("http://localhost:11434")
        self.edit_ollama_host.setMinimumWidth(400)
        layout.addRow("服务器地址:", self.edit_ollama_host)

        self.edit_ollama_model = QLineEdit()
        self.edit_ollama_model.setText("quantumcookie/sakura-galtransl-v3.7:7b")
        self.edit_ollama_model.setMinimumWidth(400)
        layout.addRow("模型名称:", self.edit_ollama_model)

        self.spin_ollama_timeout = QSpinBox()
        self.spin_ollama_timeout.setRange(30, 600)
        self.spin_ollama_timeout.setValue(120)
        self.spin_ollama_timeout.setSuffix(" 秒")
        self.spin_ollama_timeout.setMinimumWidth(150)
        layout.addRow("超时时间:", self.spin_ollama_timeout)

        self.spin_ollama_temp = QSpinBox()
        self.spin_ollama_temp.setRange(0, 100)
        self.spin_ollama_temp.setValue(3)
        self.spin_ollama_temp.setSuffix(" / 100")
        self.spin_ollama_temp.setMinimumWidth(150)
        layout.addRow("温度:", self.spin_ollama_temp)

        return widget

    def _create_lmstudio_panel(self):
        """创建 LM Studio 配置面板"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setLabelAlignment(Qt.AlignLeft)

        self.edit_lmstudio_host = QLineEdit()
        self.edit_lmstudio_host.setText("http://localhost:1234/v1")
        self.edit_lmstudio_host.setMinimumWidth(400)
        layout.addRow("服务器地址:", self.edit_lmstudio_host)

        self.edit_lmstudio_model = QLineEdit()
        self.edit_lmstudio_model.setText("sakura-galtransl-v3.7")
        self.edit_lmstudio_model.setMinimumWidth(400)
        layout.addRow("模型名称:", self.edit_lmstudio_model)

        self.spin_lmstudio_timeout = QSpinBox()
        self.spin_lmstudio_timeout.setRange(30, 600)
        self.spin_lmstudio_timeout.setValue(120)
        self.spin_lmstudio_timeout.setSuffix(" 秒")
        self.spin_lmstudio_timeout.setMinimumWidth(150)
        layout.addRow("超时时间:", self.spin_lmstudio_timeout)

        self.spin_lmstudio_temp = QSpinBox()
        self.spin_lmstudio_temp.setRange(0, 100)
        self.spin_lmstudio_temp.setValue(3)
        self.spin_lmstudio_temp.setSuffix(" / 100")
        self.spin_lmstudio_temp.setMinimumWidth(150)
        layout.addRow("温度:", self.spin_lmstudio_temp)

        return widget

    def _create_progress_tab(self):
        """创建进度选项卡"""
        from PyQt5.QtWidgets import QSplitter, QScrollArea
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        progress_scroll = QScrollArea()
        progress_scroll.setWidgetResizable(True)
        progress_scroll.setMinimumHeight(180)

        progress_panel = QWidget()
        progress_layout = QVBoxLayout(progress_panel)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(12)

        self.overall_progress = QProgressBar()
        self.overall_progress.setRange(0, 100)
        self.overall_progress.setValue(0)
        self.overall_progress.setMinimumHeight(35)
        self.overall_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3d3d5c;
                border-radius: 8px;
                background: #2d2d4a;
            }
            QProgressBar::chunk {
                background-color: #7c6fdc;
                border-radius: 6px;
            }
        """)
        progress_layout.addWidget(self.overall_progress)

        progress_info = QLabel("等待开始...")
        progress_info.setStyleSheet("font-weight: bold; color: #7c6fdc; font-size: 20px;")
        progress_layout.addWidget(progress_info)

        info_group = QGroupBox("处理信息")
        info_group.setStyleSheet("font-size: 20px;")
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(8)
        info_layout.setLabelAlignment(Qt.AlignLeft)

        self.current_video_label = QLabel("无")
        self.current_video_label.setStyleSheet("font-size: 20px;")
        info_layout.addRow("当前视频:", self.current_video_label)

        self.current_stage_label = QLabel("等待中")
        self.current_stage_label.setStyleSheet("font-size: 20px;")
        info_layout.addRow("当前阶段:", self.current_stage_label)

        self.progress_detail_label = QLabel("0 / 0")
        self.progress_detail_label.setStyleSheet("font-size: 20px;")
        info_layout.addRow("总体进度:", self.progress_detail_label)

        self.estimated_time_label = QLabel("--")
        self.estimated_time_label.setStyleSheet("font-size: 20px;")
        info_layout.addRow("预计剩余时间:", self.estimated_time_label)

        self.processing_speed_label = QLabel("--")
        self.processing_speed_label.setStyleSheet("font-size: 20px;")
        info_layout.addRow("处理速度:", self.processing_speed_label)

        progress_layout.addWidget(info_group)

        stage_group = QGroupBox("阶段进度")
        stage_group.setStyleSheet("font-size: 20px;")
        stage_layout = QVBoxLayout(stage_group)
        stage_layout.setSpacing(8)

        self.stage_progress = QProgressBar()
        self.stage_progress.setRange(0, 100)
        self.stage_progress.setValue(0)
        self.stage_progress.setMinimumHeight(30)
        self.stage_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3d3d5c;
                border-radius: 6px;
                background: #2d2d4a;
            }
            QProgressBar::chunk {
                background-color: #69f0ae;
                border-radius: 4px;
            }
        """)
        stage_layout.addWidget(self.stage_progress)

        self.stage_info_label = QLabel("OCR识别: 0% → 翻译处理: 0% → 字幕生成: 0% → 视频合成: 0%")
        self.stage_info_label.setStyleSheet("font-size: 18px;")
        stage_layout.addWidget(self.stage_info_label)

        progress_layout.addWidget(stage_group)

        progress_scroll.setWidget(progress_panel)

        video_panel = QWidget()
        video_layout = QVBoxLayout(video_panel)
        video_layout.setContentsMargins(0, 0, 0, 0)

        video_group = QGroupBox("视频列表")
        video_group.setStyleSheet("font-size: 20px;")
        video_group_layout = QVBoxLayout(video_group)

        self.video_list = QTableWidget()
        self.video_list.setColumnCount(3)
        self.video_list.setHorizontalHeaderLabels(["文件名", "状态", "进度"])
        self.video_list.setColumnWidth(0, 400)
        self.video_list.setColumnWidth(1, 100)
        self.video_list.setColumnWidth(2, 100)
        self.video_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.video_list.setMinimumHeight(150)
        video_group_layout.addWidget(self.video_list)

        video_layout.addWidget(video_group)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(progress_scroll)
        splitter.addWidget(video_panel)
        splitter.setSizes([220, 200])

        layout.addWidget(splitter)

        return widget

    def setup_components(self, config_manager, video_manager, engine):
        """设置组件"""
        self.config_manager = config_manager
        self.video_manager = video_manager
        self.engine = engine

        self._load_config_to_ui()
        self.refresh_video_list()

    def _browse_input_path(self):
        """浏览输入路径"""
        folder = QFileDialog.getExistingDirectory(
            self, "选择输入目录",
            self.edit_input_path.text() or "",
            QFileDialog.ShowDirsOnly
        )
        if folder:
            self.edit_input_path.setText(folder)
            if self.config_manager:
                self.config_manager.set("paths.video_input", folder)
                self.config_manager.save()

    def _browse_output_path(self):
        """浏览输出路径"""
        folder = QFileDialog.getExistingDirectory(
            self, "选择输出目录",
            self.edit_output_path.text() or "",
            QFileDialog.ShowDirsOnly
        )
        if folder:
            self.edit_output_path.setText(folder)
            if self.config_manager:
                self.config_manager.set("paths.output_dir", folder)
                self.config_manager.save()

    def _on_framework_changed(self, index: int):
        """框架切换"""
        self.stacked_translation.setCurrentIndex(index)
        framework = "ollama" if index == 0 else "lmstudio"
        if self.config_manager:
            self.config_manager.set("translation.framework", framework)
            self.config_manager.save()
        self._reload_translator()

    def _reload_translator(self):
        """重新加载翻译器"""
        if self.engine:
            self.engine.reload_translator()

    def _on_ass_style_changed(self):
        """字幕样式改变"""
        if not self.config_manager:
            return
        font_name = self.combo_font_name.currentText()
        font_size = self.spin_subtitle_size.value()
        outline_width = self.spin_outline_width.value()
        margin_v = self.spin_margin_v.value()

        self.config_manager.set("ass_style.font_name", font_name)
        self.config_manager.set("ass_style.font_size", font_size)
        self.config_manager.set("ass_style.outline_width", outline_width)
        self.config_manager.set("ass_style.margin_v", margin_v)
        self.config_manager.save()

    def _test_translation_connection(self):
        """测试翻译连接"""
        from modules.translator import TranslatorFactory

        if not self.config_manager:
            QMessageBox.warning(self, "提示", "配置管理器未初始化")
            return

        self._save_translation_config()
        framework = "ollama" if self.combo_framework.currentIndex() == 0 else "lmstudio"
        trans_config = self.config_manager.get_translation_config()

        try:
            translator = TranslatorFactory.create(framework, trans_config)
            success, message = translator.test_connection()

            if success:
                QMessageBox.information(self, "连接测试", f"连接成功!\n\n{message}")
            else:
                QMessageBox.warning(self, "连接测试", f"连接失败\n\n{message}")
        except Exception as e:
            QMessageBox.critical(self, "连接测试", f"测试失败:\n\n{str(e)}")

    def _add_video(self):
        """添加视频"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择视频文件",
            self.edit_input_path.text() or "",
            "视频文件 (*.mp4 *.mkv *.avi *.mov *.flv *.wmv)"
        )
        if files:
            if self.video_manager:
                for file in files:
                    self.video_manager.add_video(file)
                self.refresh_video_list()

    def _remove_selected(self):
        """移除选中的视频"""
        selected_rows = self.video_list.selectionModel().selectedRows()
        if not selected_rows:
            return

        rows_to_remove = sorted([row.row() for row in selected_rows], reverse=True)
        for row in rows_to_remove:
            self.video_manager.remove_video(row)

        self.refresh_video_list()

    def refresh_video_list(self):
        """刷新视频列表"""
        if not self.video_manager:
            return

        self.video_list.setRowCount(0)
        videos = self.video_manager.get_videos()

        for i, video in enumerate(videos):
            self.video_list.insertRow(i)
            self.video_list.setItem(i, 0, QTableWidgetItem(video.name))
            self.video_list.setItem(i, 1, QTableWidgetItem(video.status_text))
            self.video_list.setItem(i, 2, QTableWidgetItem(f"{video.progress}%"))

    def _start_processing(self):
        """开始处理"""
        if not self.video_manager or not self.engine:
            return

        videos = self.video_manager.get_videos()
        if not videos:
            QMessageBox.warning(self, "提示", "请先添加视频文件")
            return

        self._save_translation_config()

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.status_bar.showMessage("处理中...")

        self.current_video_index = 0
        self._process_next_video()

    def _process_next_video(self):
        """处理下一个视频"""
        if not self.video_manager or not self.engine:
            return

        videos = self.video_manager.get_videos()
        if self.current_video_index >= len(videos):
            self._processing_finished(True, "所有视频处理完成")
            return

        video = videos[self.current_video_index]
        if video.status == VideoStatus.COMPLETED:
            self.current_video_index += 1
            self._process_next_video()
            return

        self.log_viewer.log(f"开始处理: {video.name}", LogViewer.INFO)

        self.processing_thread = ProcessingThread(self.engine, video)
        self.processing_thread.progress_updated.connect(self._on_progress_updated)
        self.processing_thread.finished.connect(self._on_video_finished)
        self.processing_thread.start()

    def _on_progress_updated(self, step, total, progress, message, eta=""):
        """进度更新（带节流机制）"""
        current_time = time.time()
        
        if current_time - self._last_progress_update < self._progress_update_interval:
            self._pending_progress = (step, total, progress, message, eta)
            return
        
        self._last_progress_update = current_time
        self._do_update_progress(step, total, progress, message, eta)
    
    def _do_update_progress(self, step, total, progress, message, eta=""):
        """执行进度更新"""
        if hasattr(self, 'overall_progress') and self.overall_progress:
            self.overall_progress.setValue(int(progress * 100))
        
        if hasattr(self, 'current_stage_label') and self.current_stage_label:
            self.current_stage_label.setText(message)
        
        if hasattr(self, 'progress_detail_label') and self.progress_detail_label:
            self.progress_detail_label.setText(f"{step} / {total}")
        
        if hasattr(self, 'estimated_time_label') and self.estimated_time_label:
            self.estimated_time_label.setText(eta if eta else "--")
        
        if self.log_viewer and message:
            self.log_viewer.log(message, LogViewer.INFO)

    def _on_video_finished(self, success, message):
        """单个视频处理完成"""
        # 确保最后一个进度更新被应用
        if self._pending_progress:
            step, total, progress, msg, eta = self._pending_progress
            self._do_update_progress(step, total, progress, msg, eta)
            self._pending_progress = None
            
        videos = self.video_manager.get_videos()
        if self.current_video_index < len(videos):
            video = videos[self.current_video_index]
            video.status = VideoStatus.COMPLETED if success else VideoStatus.FAILED
            video.progress = 100

            if success:
                self.log_viewer.log(f"完成: {video.name}", LogViewer.SUCCESS)
            else:
                self.log_viewer.log(f"失败: {video.name} - {message}", LogViewer.ERROR)

            self.refresh_video_list()

        self.current_video_index += 1

        if self.current_video_index >= len(videos):
            self._processing_finished(success, message)
        else:
            self._process_next_video()

    def _processing_finished(self, success, message):
        """处理全部完成"""
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)

        if success:
            self.status_bar.showMessage("处理完成")
            QMessageBox.information(self, "完成", "所有视频处理完成")
        else:
            self.status_bar.showMessage("处理失败")
            QMessageBox.warning(self, "失败", f"处理过程中发生错误: {message}")

    def stop_processing(self):
        """停止处理"""
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.request_cancel()
            self.processing_thread.wait(3000)
            if self.processing_thread.isRunning():
                self.processing_thread.terminate()
                self.processing_thread.wait(1000)

        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.status_bar.showMessage("已停止")

    def _clear_log(self):
        """清空日志"""
        if self.log_viewer:
            self.log_viewer.clear()

    def _load_config_to_ui(self):
        """加载配置到UI"""
        if not self.config_manager:
            return

        if self.edit_input_path:
            self.edit_input_path.setText(self.config_manager.get("paths.video_input", ""))
        if self.edit_output_path:
            self.edit_output_path.setText(self.config_manager.get("paths.output_dir", ""))

        ass_style = self.config_manager.get_ass_config()
        if self.combo_font_name:
            font_idx = self.combo_font_name.findText(ass_style.get("font_name", "Microsoft YaHei"))
            if font_idx >= 0:
                self.combo_font_name.setCurrentIndex(font_idx)
            else:
                self.combo_font_name.setCurrentText(ass_style.get("font_name", "Microsoft YaHei"))
        if self.spin_subtitle_size:
            self.spin_subtitle_size.setValue(ass_style.get("font_size", 20))
        if self.spin_outline_width:
            self.spin_outline_width.setValue(ass_style.get("outline_width", 2))
        if self.spin_margin_v:
            self.spin_margin_v.setValue(ass_style.get("margin_v", 30))

        if self.log_viewer:
            self.log_viewer.set_font_size(27)

        framework = self.config_manager.get("translation.framework", "ollama")
        index = 0 if framework == "ollama" else 1
        if self.combo_framework:
            self.combo_framework.setCurrentIndex(index)
        if self.stacked_translation:
            self.stacked_translation.setCurrentIndex(index)

        ollama = self.config_manager.get("translation.ollama", {})
        if self.edit_ollama_host:
            self.edit_ollama_host.setText(ollama.get("host", "http://localhost:11434"))
        if self.edit_ollama_model:
            self.edit_ollama_model.setText(ollama.get("model", "quantumcookie/sakura-galtransl-v3.7:7b"))
        if self.spin_ollama_timeout:
            self.spin_ollama_timeout.setValue(ollama.get("timeout", 120))
        if self.spin_ollama_temp:
            temp = ollama.get("temperature", 0.3)
            self.spin_ollama_temp.setValue(int(temp * 100))

        lmstudio = self.config_manager.get("translation.lmstudio", {})
        if self.edit_lmstudio_host:
            self.edit_lmstudio_host.setText(lmstudio.get("host", "http://localhost:1234/v1"))
        if self.edit_lmstudio_model:
            self.edit_lmstudio_model.setText(lmstudio.get("model", "sakura-galtransl-v3.7"))
        if self.spin_lmstudio_timeout:
            self.spin_lmstudio_timeout.setValue(lmstudio.get("timeout", 120))
        if self.spin_lmstudio_temp:
            temp = lmstudio.get("temperature", 0.3)
            self.spin_lmstudio_temp.setValue(int(temp * 100))

    def _save_translation_config(self):
        """保存翻译配置"""
        if not self.config_manager:
            return

        if self.combo_font_name:
            self.config_manager.set("ass_style.font_name", self.combo_font_name.currentText())
        if self.spin_subtitle_size:
            self.config_manager.set("ass_style.font_size", self.spin_subtitle_size.value())
        if self.spin_outline_width:
            self.config_manager.set("ass_style.outline_width", self.spin_outline_width.value())
        if self.spin_margin_v:
            self.config_manager.set("ass_style.margin_v", self.spin_margin_v.value())

        framework = "ollama" if self.combo_framework.currentIndex() == 0 else "lmstudio"

        if framework == "ollama":
            self.config_manager.set("translation.ollama.host", self.edit_ollama_host.text())
            self.config_manager.set("translation.ollama.model", self.edit_ollama_model.text())
            self.config_manager.set("translation.ollama.timeout", self.spin_ollama_timeout.value())
            self.config_manager.set("translation.ollama.temperature", self.spin_ollama_temp.value() / 100)
        else:
            self.config_manager.set("translation.lmstudio.host", self.edit_lmstudio_host.text())
            self.config_manager.set("translation.lmstudio.model", self.edit_lmstudio_model.text())
            self.config_manager.set("translation.lmstudio.timeout", self.spin_lmstudio_timeout.value())
            self.config_manager.set("translation.lmstudio.temperature", self.spin_lmstudio_temp.value() / 100)

        self.config_manager.set("translation.framework", framework)

        self.config_manager.save()

    def _reset_config(self):
        """重置配置"""
        reply = QMessageBox.question(
            self, "确认重置",
            "确定要重置所有配置吗?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.config_manager:
                self.config_manager.reset_to_default()
                self._load_config_to_ui()
            QMessageBox.information(self, "重置完成", "配置已重置为默认值")

    def _show_about(self):
        """显示关于信息"""
        about_text = """
AVT字幕处理器 v1.0.0

一款用于提取日文字幕并翻译成中文的工具。

功能特性:
- 支持 Ollama 和 LM Studio 双框架
- GPU加速的OCR文字识别
- 智能字幕时间轴生成
- 高质量字幕烧录

技术支持:
- PyQt5
- PaddleOCR
- FFmpeg
"""
        QMessageBox.about(self, "关于", about_text)

    def closeEvent(self, event):
        """关闭事件"""
        self._save_translation_config()

        if self.processing_thread and self.processing_thread.isRunning():
            reply = QMessageBox.question(
                self, '确认退出',
                "正在处理中,确定要退出吗?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.processing_thread.request_cancel()
                self.processing_thread.wait(3000)
                if self.processing_thread.isRunning():
                    self.processing_thread.terminate()
                    self.processing_thread.wait(1000)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

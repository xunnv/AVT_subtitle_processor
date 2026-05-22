"""
日志查看器模块
显示处理日志和状态信息
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QPushButton, QCheckBox, QLabel, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QMutex, QTimer
from PyQt5.QtGui import QTextCharFormat, QColor, QFont, QTextCursor
from datetime import datetime
import threading


class LogEmitter(QObject):
    """日志发射器"""
    log_signal = pyqtSignal(str, str)


class LogViewer(QWidget):
    """日志查看器类"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

    def __init__(self, max_lines: int = 1000):
        super().__init__()
        self.max_lines = max_lines
        self.mutex = QMutex()
        self.emitter = LogEmitter()
        self.emitter.log_signal.connect(self.append_log)
        self.log_font_size = 27
        
        self._log_buffer = []
        self._html_cache = ""
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._flush_buffer)
        self._update_timer.setInterval(100)
        
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        toolbar = QHBoxLayout()

        self.chk_auto_scroll = QCheckBox("自动滚动")
        self.chk_auto_scroll.setChecked(True)

        self.chk_show_info = QCheckBox("信息")
        self.chk_show_info.setChecked(True)
        self.chk_show_info.setStyleSheet("""
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 1.5px solid #4d4d6c;
                background: #1a1a2e;
            }
            QCheckBox::indicator:checked {
                background: #7c6fdc;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEgNUw0LjUgOSA1MSIvPjwvc3ZnPg==);
                border-color: #9d8fdf;
            }
        """)
        self.chk_show_info.stateChanged.connect(self._on_filter_changed)

        self.chk_show_warning = QCheckBox("警告")
        self.chk_show_warning.setChecked(True)
        self.chk_show_warning.setStyleSheet("""
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 1.5px solid #4d4d6c;
                background: #1a1a2e;
            }
            QCheckBox::indicator:checked {
                background: #ffc107;
                border-color: #ffca28;
            }
        """)
        self.chk_show_warning.stateChanged.connect(self._on_filter_changed)

        self.chk_show_error = QCheckBox("错误")
        self.chk_show_error.setChecked(True)
        self.chk_show_error.setStyleSheet("""
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 1.5px solid #4d4d6c;
                background: #1a1a2e;
            }
            QCheckBox::indicator:checked {
                background: #ff5252;
                border-color: #ff7043;
            }
        """)
        self.chk_show_error.stateChanged.connect(self._on_filter_changed)

        self.chk_show_success = QCheckBox("成功")
        self.chk_show_success.setChecked(True)
        self.chk_show_success.setStyleSheet("""
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 1.5px solid #4d4d6c;
                background: #1a1a2e;
            }
            QCheckBox::indicator:checked {
                background: #69f0ae;
                border-color: #69f0ae;
            }
        """)
        self.chk_show_success.stateChanged.connect(self._on_filter_changed)

        btn_clear = QPushButton("清空")
        btn_clear.clicked.connect(self.clear)

        btn_save = QPushButton("保存日志")
        btn_save.clicked.connect(self.save_log)

        toolbar.addWidget(QLabel("显示:"))
        toolbar.addWidget(self.chk_show_info)
        toolbar.addWidget(self.chk_show_warning)
        toolbar.addWidget(self.chk_show_error)
        toolbar.addWidget(self.chk_show_success)
        toolbar.addStretch()
        toolbar.addWidget(self.chk_auto_scroll)
        toolbar.addWidget(btn_clear)
        toolbar.addWidget(btn_save)

        main_layout.addLayout(toolbar)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)

        font = QFont("Consolas", self.log_font_size)
        self.log_text.setFont(font)

        main_layout.addWidget(self.log_text)

        status_layout = QHBoxLayout()
        self.line_count_label = QLabel("行数: 0")
        self.filtered_label = QLabel("已过滤: 0")
        status_layout.addWidget(self.line_count_label)
        status_layout.addWidget(self.filtered_label)
        status_layout.addStretch()

        main_layout.addLayout(status_layout)

    def set_font_size(self, size: int):
        """设置日志字体大小"""
        self.log_font_size = size
        font = QFont("Consolas", size)
        self.log_text.setFont(font)

    def _on_filter_changed(self):
        """过滤条件改变"""
        pass

    def _generate_html(self, message: str, level: str) -> str:
        """生成日志HTML"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if level == self.INFO:
            color = "#c0c0c0"
            prefix = "[INFO]"
        elif level == self.WARNING:
            color = "#ffc107"
            prefix = "[WARN]"
        elif level == self.ERROR:
            color = "#ff5252"
            prefix = "[ERROR]"
        elif level == self.SUCCESS:
            color = "#69f0ae"
            prefix = "[OK]"
        else:
            color = "#c0c0c0"
            prefix = ""
        
        return f'<span style="color: #606060;">[{timestamp}]</span> <span style="color: {color};">{prefix} {message}</span>'

    def append_log(self, message: str, level: str = INFO):
        """追加日志（批量缓冲）"""
        self.mutex.lock()
        
        try:
            html = self._generate_html(message, level)
            self._log_buffer.append(html)
            
            if not self._update_timer.isActive():
                self._update_timer.start()
        finally:
            self.mutex.unlock()

    def _flush_buffer(self):
        """批量刷新日志缓冲区"""
        self.mutex.lock()
        
        try:
            if not self._log_buffer:
                self._update_timer.stop()
                return
            
            buffer_to_flush = self._log_buffer
            self._log_buffer = []
            
            if not buffer_to_flush:
                return
            
            html_batch = "<br>".join(buffer_to_flush) + "<br>"
            
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertHtml(html_batch)
            
            if self.chk_auto_scroll.isChecked():
                scrollbar = self.log_text.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
            
            lines = self.log_text.document().blockCount()
            self.line_count_label.setText(f"行数: {lines}")
            
            if lines > self.max_lines:
                self._trim_lines()
                
        finally:
            self.mutex.unlock()

    def log(self, message: str, level: str = INFO):
        """添加日志（线程安全）"""
        self.emitter.log_signal.emit(message, level)

    def log_error(self, message: str):
        """添加错误日志并立即刷新"""
        self.log(message, self.ERROR)
        self._flush_buffer()
    
    def log_success(self, message: str):
        """添加成功日志并立即刷新"""
        self.log(message, self.SUCCESS)
        self._flush_buffer()

    def info(self, message: str):
        """添加信息日志"""
        self.log(message, self.INFO)

    def warning(self, message: str):
        """添加警告日志"""
        self.log(message, self.WARNING)

    def error(self, message: str):
        """添加错误日志"""
        self.log(message, self.ERROR)

    def success(self, message: str):
        """添加成功日志"""
        self.log(message, self.SUCCESS)

    def _trim_lines(self):
        """裁剪超出的行数"""
        cursor = QTextCursor(self.log_text.document())
        cursor.movePosition(QTextCursor.Start)
        cursor.select(QTextCursor.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.deleteChar()

    def clear(self):
        """清空日志"""
        self.log_text.clear()
        self.line_count_label.setText("行数: 0")

    def save_log(self, filepath: str = None):
        """保存日志"""
        if filepath is None:
            from PyQt5.QtWidgets import QFileDialog
            filepath, _ = QFileDialog.getSaveFileName(
                self, "保存日志",
                f"avt_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "文本文件 (*.txt);;所有文件 (*)"
            )
            if not filepath:
                return

        try:
            plain_text = self.log_text.toPlainText()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(plain_text)
            self.success(f"日志已保存: {filepath}")
        except Exception as e:
            self.error(f"保存日志失败: {e}")

    def get_log_text(self) -> str:
        """获取日志文本"""
        return self.log_text.toPlainText()

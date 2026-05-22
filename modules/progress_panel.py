"""
进度面板模块
显示处理进度和状态信息
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QProgressBar, QTextEdit, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QTextCharFormat, QTextCursor


class ProgressPanel(QWidget):
    """进度面板类"""

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #252536;")
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 总体进度组
        main_layout.addWidget(self._create_overall_group())

        # 当前视频进度组
        main_layout.addWidget(self._create_current_video_group())

        # 统计信息组
        main_layout.addWidget(self._create_statistics_group())

        main_layout.addStretch()

    def _create_overall_group(self) -> QGroupBox:
        """创建总体进度组"""
        group = QGroupBox("📊 总体进度")
        layout = QVBoxLayout()

        self.overall_progress = QProgressBar()
        self.overall_progress.setMinimum(0)
        self.overall_progress.setMaximum(100)
        self.overall_progress.setValue(0)
        self.overall_progress.setTextVisible(True)
        self.overall_progress.setFormat("%p%")

        self.overall_label = QLabel("等待处理...")
        self.overall_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.overall_progress)
        layout.addWidget(self.overall_label)

        group.setLayout(layout)
        return group

    def _create_current_video_group(self) -> QGroupBox:
        """创建当前视频进度组"""
        group = QGroupBox("🎬 当前视频")
        layout = QVBoxLayout()

        self.current_video_label = QLabel("无")
        self.current_video_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #e0e0e0;")

        self.current_progress = QProgressBar()
        self.current_progress.setMinimum(0)
        self.current_progress.setMaximum(100)
        self.current_progress.setValue(0)

        self.current_step_label = QLabel("等待开始...")
        self.current_step_label.setAlignment(Qt.AlignCenter)

        info_layout = QHBoxLayout()
        self.eta_label = QLabel("预计剩余: --")
        self.speed_label = QLabel("速度: --")
        info_layout.addWidget(self.eta_label)
        info_layout.addWidget(self.speed_label)

        layout.addWidget(self.current_video_label)
        layout.addWidget(self.current_progress)
        layout.addWidget(self.current_step_label)
        layout.addLayout(info_layout)

        group.setLayout(layout)
        return group

    def _create_statistics_group(self) -> QGroupBox:
        """创建统计信息组"""
        group = QGroupBox("📈 处理统计")
        layout = QGridLayout()

        self.stat_total = QLabel("0")
        self.stat_pending = QLabel("0")
        self.stat_processing = QLabel("0")
        self.stat_completed = QLabel("0")
        self.stat_failed = QLabel("0")
        self.stat_rate = QLabel("0 个/小时")

        layout.addWidget(QLabel("总视频数:"), 0, 0)
        layout.addWidget(self.stat_total, 0, 1)
        layout.addWidget(QLabel("待处理:"), 0, 2)
        layout.addWidget(self.stat_pending, 0, 3)

        layout.addWidget(QLabel("处理中:"), 1, 0)
        layout.addWidget(self.stat_processing, 1, 1)
        layout.addWidget(QLabel("已完成:"), 1, 2)
        layout.addWidget(self.stat_completed, 1, 3)

        layout.addWidget(QLabel("失败:"), 2, 0)
        layout.addWidget(self.stat_failed, 2, 1)
        layout.addWidget(QLabel("处理速率:"), 2, 2)
        layout.addWidget(self.stat_rate, 2, 3)

        group.setLayout(layout)
        return group

    def update_overall(self, completed: int, total: int):
        """更新总体进度"""
        if total > 0:
            percentage = int(completed / total * 100)
            self.overall_progress.setValue(percentage)
            self.overall_label.setText(f"已完成: {completed} / {total}")
        else:
            self.overall_progress.setValue(0)
            self.overall_label.setText("等待处理...")

    def update_current_video(self, video_name: str, progress: float,
                           step: str, step_progress: float, eta: str = ""):
        """更新当前视频进度"""
        self.current_video_label.setText(f"📹 {video_name}")
        self.current_progress.setValue(int(step_progress))
        self.current_step_label.setText(step)
        self.eta_label.setText(f"预计剩余: {eta}" if eta else "预计剩余: --")

    def update_step(self, step_num: int, total_steps: int, message: str):
        """更新步骤信息"""
        self.current_step_label.setText(f"步骤 {step_num}/{total_steps}: {message}")

    def update_statistics(self, stats: dict):
        """更新统计数据"""
        self.stat_total.setText(str(stats.get('total', 0)))
        self.stat_pending.setText(str(stats.get('pending', 0)))
        self.stat_processing.setText(str(stats.get('processing', 0)))
        self.stat_completed.setText(str(stats.get('completed', 0)))
        self.stat_failed.setText(str(stats.get('failed', 0)))

    def update_rate(self, rate: float):
        """更新处理速率"""
        self.stat_rate.setText(f"{rate:.1f} 个/小时")

    def set_idle(self):
        """设置空闲状态"""
        self.current_video_label.setText("无")
        self.current_progress.setValue(0)
        self.current_step_label.setText("等待开始...")
        self.eta_label.setText("预计剩余: --")
        self.speed_label.setText("速度: --")

    def set_processing(self, video_name: str):
        """设置处理状态"""
        self.current_video_label.setText(f"📹 {video_name}")
        self.current_progress.setValue(0)
        self.current_step_label.setText("准备中...")

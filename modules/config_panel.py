"""
配置面板模块
提供可视化的配置界面
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
                             QCheckBox, QComboBox, QGroupBox, QPushButton,
                             QFileDialog, QFormLayout, QScrollArea, QStackedWidget,
                             QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal


class ConfigPanel(QWidget):
    """配置面板类"""

    config_changed = pyqtSignal()

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        content_layout.addWidget(self._create_path_group())
        content_layout.addWidget(self._create_translation_group())
        content_layout.addWidget(self._create_ocr_group())
        content_layout.addWidget(self._create_subtitle_group())
        content_layout.addWidget(self._create_ass_style_group())
        content_layout.addWidget(self._create_burn_group())

        content_layout.addStretch()

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _create_path_group(self) -> QGroupBox:
        """创建路径配置组"""
        group = QGroupBox("路径配置")
        layout = QFormLayout()

        self.path_video_input = QLineEdit()
        self.path_video_input.setText(self.config.get('paths.video_input', ''))
        self.path_video_input.textChanged.connect(self._on_config_changed)

        btn_browse_input = QPushButton("浏览...")
        btn_browse_input.clicked.connect(lambda: self._browse_path('paths.video_input', self.path_video_input))

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.path_video_input)
        input_layout.addWidget(btn_browse_input)

        self.path_output_dir = QLineEdit()
        self.path_output_dir.setText(self.config.get('paths.output_dir', ''))
        self.path_output_dir.textChanged.connect(self._on_config_changed)

        btn_browse_output = QPushButton("浏览...")
        btn_browse_output.clicked.connect(lambda: self._browse_path('paths.output_dir', self.path_output_dir))

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.path_output_dir)
        output_layout.addWidget(btn_browse_output)

        layout.addRow("视频输入目录:", input_layout)
        layout.addRow("输出目录:", output_layout)

        group.setLayout(layout)
        return group

    def _create_translation_group(self) -> QGroupBox:
        """创建翻译配置组"""
        group = QGroupBox("翻译配置")
        layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("翻译框架:"))
        self.combo_framework = QComboBox()
        self.combo_framework.addItems(["Ollama", "LM Studio"])
        framework = self.config.get('translation.framework', 'ollama')
        index = 0 if framework.lower() == 'ollama' else 1
        self.combo_framework.setCurrentIndex(index)
        self.combo_framework.currentIndexChanged.connect(self._on_framework_changed)
        top_layout.addWidget(self.combo_framework)

        btn_test = QPushButton("测试连接")
        btn_test.clicked.connect(self._test_connection)
        top_layout.addWidget(btn_test)
        top_layout.addStretch()

        layout.addLayout(top_layout)

        self.stacked_translation = QStackedWidget()

        self.ollama_panel = self._create_ollama_panel()
        self.lmstudio_panel = self._create_lmstudio_panel()

        self.stacked_translation.addWidget(self.ollama_panel)
        self.stacked_translation.addWidget(self.lmstudio_panel)
        self.stacked_translation.setCurrentIndex(index)

        layout.addWidget(self.stacked_translation)

        group.setLayout(layout)
        return group

    def _create_ollama_panel(self) -> QWidget:
        """创建 Ollama 配置面板"""
        widget = QWidget()
        layout = QGridLayout()

        layout.addWidget(QLabel("API 地址:"), 0, 0)
        self.edit_ollama_host = QLineEdit()
        self.edit_ollama_host.setText(self.config.get('translation.ollama.host', 'http://localhost:11434'))
        self.edit_ollama_host.textChanged.connect(self._on_config_changed)
        layout.addWidget(self.edit_ollama_host, 0, 1)

        layout.addWidget(QLabel("模型名称:"), 1, 0)
        self.edit_ollama_model = QLineEdit()
        self.edit_ollama_model.setText(self.config.get('translation.ollama.model', 'quantumcookie/sakura-galtransl-v3.7:7b'))
        self.edit_ollama_model.textChanged.connect(self._on_config_changed)
        layout.addWidget(self.edit_ollama_model, 1, 1)

        layout.addWidget(QLabel("超时(秒):"), 2, 0)
        self.spin_ollama_timeout = QSpinBox()
        self.spin_ollama_timeout.setRange(30, 600)
        self.spin_ollama_timeout.setSingleStep(10)
        self.spin_ollama_timeout.setValue(self.config.get('translation.ollama.timeout', 120))
        self.spin_ollama_timeout.valueChanged.connect(self._on_config_changed)
        layout.addWidget(self.spin_ollama_timeout, 2, 1)

        layout.addWidget(QLabel("温度参数:"), 3, 0)
        self.spin_ollama_temp = QDoubleSpinBox()
        self.spin_ollama_temp.setRange(0.0, 1.0)
        self.spin_ollama_temp.setSingleStep(0.05)
        self.spin_ollama_temp.setValue(self.config.get('translation.ollama.temperature', 0.3))
        self.spin_ollama_temp.valueChanged.connect(self._on_config_changed)
        layout.addWidget(self.spin_ollama_temp, 3, 1)

        layout.addWidget(QLabel("重试次数:"), 4, 0)
        self.spin_ollama_retries = QSpinBox()
        self.spin_ollama_retries.setRange(1, 10)
        self.spin_ollama_retries.setValue(self.config.get('translation.ollama.max_retries', 3))
        self.spin_ollama_retries.valueChanged.connect(self._on_config_changed)
        layout.addWidget(self.spin_ollama_retries, 4, 1)

        widget.setLayout(layout)
        return widget

    def _create_lmstudio_panel(self) -> QWidget:
        """创建 LM Studio 配置面板"""
        widget = QWidget()
        layout = QGridLayout()

        layout.addWidget(QLabel("API 地址:"), 0, 0)
        self.edit_lmstudio_host = QLineEdit()
        self.edit_lmstudio_host.setText(self.config.get('translation.lmstudio.host', 'http://localhost:1234/v1'))
        self.edit_lmstudio_host.textChanged.connect(self._on_config_changed)
        layout.addWidget(self.edit_lmstudio_host, 0, 1)

        layout.addWidget(QLabel("模型名称:"), 1, 0)
        self.edit_lmstudio_model = QLineEdit()
        self.edit_lmstudio_model.setText(self.config.get('translation.lmstudio.model', 'sakura-galtransl-v3.7'))
        self.edit_lmstudio_model.textChanged.connect(self._on_config_changed)
        layout.addWidget(self.edit_lmstudio_model, 1, 1)

        layout.addWidget(QLabel("超时(秒):"), 2, 0)
        self.spin_lmstudio_timeout = QSpinBox()
        self.spin_lmstudio_timeout.setRange(30, 600)
        self.spin_lmstudio_timeout.setSingleStep(10)
        self.spin_lmstudio_timeout.setValue(self.config.get('translation.lmstudio.timeout', 120))
        self.spin_lmstudio_timeout.valueChanged.connect(self._on_config_changed)
        layout.addWidget(self.spin_lmstudio_timeout, 2, 1)

        layout.addWidget(QLabel("温度参数:"), 3, 0)
        self.spin_lmstudio_temp = QDoubleSpinBox()
        self.spin_lmstudio_temp.setRange(0.0, 1.0)
        self.spin_lmstudio_temp.setSingleStep(0.05)
        self.spin_lmstudio_temp.setValue(self.config.get('translation.lmstudio.temperature', 0.3))
        self.spin_lmstudio_temp.valueChanged.connect(self._on_config_changed)
        layout.addWidget(self.spin_lmstudio_temp, 3, 1)

        layout.addWidget(QLabel("重试次数:"), 4, 0)
        self.spin_lmstudio_retries = QSpinBox()
        self.spin_lmstudio_retries.setRange(1, 10)
        self.spin_lmstudio_retries.setValue(self.config.get('translation.lmstudio.max_retries', 3))
        self.spin_lmstudio_retries.valueChanged.connect(self._on_config_changed)
        layout.addWidget(self.spin_lmstudio_retries, 4, 1)

        widget.setLayout(layout)
        return widget

    def _on_framework_changed(self, index: int):
        """框架切换"""
        self.stacked_translation.setCurrentIndex(index)
        framework = "ollama" if index == 0 else "lmstudio"
        self.config.set('translation.framework', framework)
        self.config.save()
        self.config_changed.emit()

    def _test_connection(self):
        """测试连接"""
        from modules.translator import TranslatorFactory

        framework = "ollama" if self.combo_framework.currentIndex() == 0 else "lmstudio"
        trans_config = self.config.get_translation_config()

        try:
            translator = TranslatorFactory.create(framework, trans_config)
            success, message = translator.test_connection()

            if success:
                QMessageBox.information(self, "连接测试", f"连接成功!\n{message}")
            else:
                QMessageBox.warning(self, "连接测试", f"连接失败\n{message}")
        except Exception as e:
            QMessageBox.critical(self, "连接测试", f"测试失败:\n{str(e)}")

    def _create_ocr_group(self) -> QGroupBox:
        """创建OCR配置组"""
        group = QGroupBox("OCR配置")
        layout = QGridLayout()

        self.chk_use_gpu = QCheckBox("使用GPU加速")
        self.chk_use_gpu.setChecked(self.config.get('ocr.use_gpu', True))
        self.chk_use_gpu.stateChanged.connect(self._on_config_changed)

        self.spin_det_thresh = QDoubleSpinBox()
        self.spin_det_thresh.setRange(0.1, 1.0)
        self.spin_det_thresh.setSingleStep(0.05)
        self.spin_det_thresh.setValue(self.config.get('ocr.det_db_thresh', 0.3))
        self.spin_det_thresh.valueChanged.connect(self._on_config_changed)

        self.spin_rec_thresh = QDoubleSpinBox()
        self.spin_rec_thresh.setRange(0.1, 1.0)
        self.spin_rec_thresh.setSingleStep(0.05)
        self.spin_rec_thresh.setValue(self.config.get('ocr.rec_score_thresh', 0.5))
        self.spin_rec_thresh.valueChanged.connect(self._on_config_changed)

        self.spin_frame_interval = QSpinBox()
        self.spin_frame_interval.setRange(1, 10)
        self.spin_frame_interval.setValue(self.config.get('ocr.frame_interval', 1))
        self.spin_frame_interval.valueChanged.connect(self._on_config_changed)

        layout.addWidget(QLabel("GPU加速:"), 0, 0)
        layout.addWidget(self.chk_use_gpu, 0, 1)
        layout.addWidget(QLabel("检测阈值:"), 1, 0)
        layout.addWidget(self.spin_det_thresh, 1, 1)
        layout.addWidget(QLabel("识别置信度:"), 2, 0)
        layout.addWidget(self.spin_rec_thresh, 2, 1)
        layout.addWidget(QLabel("帧间隔(秒):"), 3, 0)
        layout.addWidget(self.spin_frame_interval, 3, 1)

        group.setLayout(layout)
        return group

    def _create_subtitle_group(self) -> QGroupBox:
        """创建字幕配置组"""
        group = QGroupBox("字幕整理配置")
        layout = QGridLayout()

        self.spin_min_length = QSpinBox()
        self.spin_min_length.setRange(1, 10)
        self.spin_min_length.setValue(self.config.get('subtitle.min_length', 2))
        self.spin_min_length.valueChanged.connect(self._on_config_changed)

        self.spin_max_gap = QDoubleSpinBox()
        self.spin_max_gap.setRange(0.5, 10.0)
        self.spin_max_gap.setSingleStep(0.5)
        self.spin_max_gap.setValue(self.config.get('subtitle.max_gap', 3.0))
        self.spin_max_gap.valueChanged.connect(self._on_config_changed)

        self.spin_max_duration = QDoubleSpinBox()
        self.spin_max_duration.setRange(5.0, 120.0)
        self.spin_max_duration.setSingleStep(5.0)
        self.spin_max_duration.setValue(self.config.get('subtitle.max_duration', 30.0))
        self.spin_max_duration.valueChanged.connect(self._on_config_changed)

        self.spin_similarity = QDoubleSpinBox()
        self.spin_similarity.setRange(0.5, 1.0)
        self.spin_similarity.setSingleStep(0.05)
        self.spin_similarity.setValue(self.config.get('subtitle.similarity_threshold', 0.8))
        self.spin_similarity.valueChanged.connect(self._on_config_changed)

        self.chk_translation_only = QCheckBox("仅显示译文字幕")
        self.chk_translation_only.setChecked(self.config.get('subtitle.show_translation_only', False))
        self.chk_translation_only.stateChanged.connect(self._on_config_changed)

        layout.addWidget(QLabel("最短字符数:"), 0, 0)
        layout.addWidget(self.spin_min_length, 0, 1)
        layout.addWidget(QLabel("最大间隔(秒):"), 1, 0)
        layout.addWidget(self.spin_max_gap, 1, 1)
        layout.addWidget(QLabel("最大时长(秒):"), 2, 0)
        layout.addWidget(self.spin_max_duration, 2, 1)
        layout.addWidget(QLabel("相似度阈值:"), 3, 0)
        layout.addWidget(self.spin_similarity, 3, 1)
        layout.addWidget(self.chk_translation_only, 4, 0, 1, 2)

        group.setLayout(layout)
        return group

    def _create_ass_style_group(self) -> QGroupBox:
        """创建ASS样式配置组"""
        group = QGroupBox("ASS字幕样式")
        layout = QGridLayout()

        self.combo_font = QComboBox()
        self.combo_font.addItems([
            "Microsoft YaHei",
            "SimHei",
            "Arial",
            "Times New Roman"
        ])
        current_font = self.config.get('ass_style.font_name', 'Microsoft YaHei')
        index = self.combo_font.findText(current_font)
        if index >= 0:
            self.combo_font.setCurrentIndex(index)
        self.combo_font.currentTextChanged.connect(self._on_config_changed)

        self.spin_font_size = QSpinBox()
        self.spin_font_size.setRange(10, 50)
        self.spin_font_size.setValue(self.config.get('ass_style.font_size', 20))
        self.spin_font_size.valueChanged.connect(self._on_config_changed)

        self.spin_outline = QSpinBox()
        self.spin_outline.setRange(0, 5)
        self.spin_outline.setValue(self.config.get('ass_style.outline_width', 2))
        self.spin_outline.valueChanged.connect(self._on_config_changed)

        self.spin_margin = QSpinBox()
        self.spin_margin.setRange(10, 100)
        self.spin_margin.setValue(self.config.get('ass_style.margin_v', 30))
        self.spin_margin.valueChanged.connect(self._on_config_changed)

        layout.addWidget(QLabel("字体:"), 0, 0)
        layout.addWidget(self.combo_font, 0, 1)
        layout.addWidget(QLabel("字体大小:"), 1, 0)
        layout.addWidget(self.spin_font_size, 1, 1)
        layout.addWidget(QLabel("描边宽度:"), 2, 0)
        layout.addWidget(self.spin_outline, 2, 1)
        layout.addWidget(QLabel("底部边距:"), 3, 0)
        layout.addWidget(self.spin_margin, 3, 1)

        group.setLayout(layout)
        return group

    def _create_burn_group(self) -> QGroupBox:
        """创建烧录配置组"""
        group = QGroupBox("视频烧录配置")
        layout = QGridLayout()

        self.combo_preset = QComboBox()
        self.combo_preset.addItems([
            "p1 (最快)",
            "p2",
            "p3",
            "p4 (平衡)",
            "p5",
            "p6",
            "p7 (最高质量)"
        ])
        preset = self.config.get('burn.preset', 'p4')
        index = self.combo_preset.findText(preset)
        if index < 0:
            index = 3
        self.combo_preset.setCurrentIndex(index)
        self.combo_preset.currentTextChanged.connect(self._on_config_changed)

        self.spin_crf = QSpinBox()
        self.spin_crf.setRange(18, 28)
        self.spin_crf.setValue(self.config.get('burn.crf', 23))
        self.spin_crf.valueChanged.connect(self._on_config_changed)

        layout.addWidget(QLabel("编码预设:"), 0, 0)
        layout.addWidget(self.combo_preset, 0, 1)
        layout.addWidget(QLabel("质量因子(CRF):"), 1, 0)
        layout.addWidget(self.spin_crf, 1, 1)

        note = QLabel("提示: CRF值越低质量越好，文件越大")
        note.setStyleSheet("color: #808080; font-size: 10px;")
        layout.addWidget(note, 2, 0, 1, 2)

        group.setLayout(layout)
        return group

    def _browse_path(self, config_key: str, line_edit: QLineEdit):
        """浏览路径"""
        current = line_edit.text()
        folder = QFileDialog.getExistingDirectory(
            self, "选择目录", current,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            line_edit.setText(folder)
            self.config.set(config_key, folder)
            self.config.save()

    def _on_config_changed(self):
        """配置改变处理"""
        self._save_config()
        self.config_changed.emit()

    def _save_config(self):
        """保存配置"""
        self.config.set('paths.video_input', self.path_video_input.text())
        self.config.set('paths.output_dir', self.path_output_dir.text())

        self.config.set('ocr.use_gpu', self.chk_use_gpu.isChecked())
        self.config.set('ocr.det_db_thresh', self.spin_det_thresh.value())
        self.config.set('ocr.rec_score_thresh', self.spin_rec_thresh.value())
        self.config.set('ocr.frame_interval', self.spin_frame_interval.value())

        self.config.set('subtitle.min_length', self.spin_min_length.value())
        self.config.set('subtitle.max_gap', self.spin_max_gap.value())
        self.config.set('subtitle.max_duration', self.spin_max_duration.value())
        self.config.set('subtitle.similarity_threshold', self.spin_similarity.value())
        self.config.set('subtitle.show_translation_only', self.chk_translation_only.isChecked())

        framework = "ollama" if self.combo_framework.currentIndex() == 0 else "lmstudio"
        self.config.set('translation.framework', framework)

        self.config.set('translation.ollama.host', self.edit_ollama_host.text())
        self.config.set('translation.ollama.model', self.edit_ollama_model.text())
        self.config.set('translation.ollama.timeout', self.spin_ollama_timeout.value())
        self.config.set('translation.ollama.temperature', self.spin_ollama_temp.value())
        self.config.set('translation.ollama.max_retries', self.spin_ollama_retries.value())

        self.config.set('translation.lmstudio.host', self.edit_lmstudio_host.text())
        self.config.set('translation.lmstudio.model', self.edit_lmstudio_model.text())
        self.config.set('translation.lmstudio.timeout', self.spin_lmstudio_timeout.value())
        self.config.set('translation.lmstudio.temperature', self.spin_lmstudio_temp.value())
        self.config.set('translation.lmstudio.max_retries', self.spin_lmstudio_retries.value())

        self.config.set('ass_style.font_name', self.combo_font.currentText())
        self.config.set('ass_style.font_size', self.spin_font_size.value())
        self.config.set('ass_style.outline_width', self.spin_outline.value())
        self.config.set('ass_style.margin_v', self.spin_margin.value())

        preset_text = self.combo_preset.currentText()
        preset = preset_text.split(" ")[0]
        self.config.set('burn.preset', preset)
        self.config.set('burn.crf', self.spin_crf.value())

        self.config.save()

    def refresh(self):
        """刷新配置显示"""
        self.path_video_input.setText(self.config.get('paths.video_input', ''))
        self.path_output_dir.setText(self.config.get('paths.output_dir', ''))

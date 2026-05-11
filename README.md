# AVT字幕处理器

一个基于 PyQt5 开发的 Windows 桌面应用程序，用于日语视频字幕提取、翻译和烧录。

## 功能特性

- **字幕提取**: 使用 PaddleOCR GPU 自动识别视频中的日语字幕
- **智能翻译**: 使用 Ollama 本地模型进行日→中翻译
- **高质量烧录**: 使用 NVENC GPU 硬件编码烧录字幕到视频
- **批量处理**: 支持多个视频队列处理
- **断点续传**: 自动检测已完成的步骤，跳过处理
- **实时监控**: 实时显示处理进度和状态

## 环境要求

- Windows 10/11 (64位)
- Python 3.10+
- NVIDIA GPU (支持 CUDA 11.x)
- 16GB+ RAM

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/XUNNV/AVT_subtitle_processor.git
cd AVT_subtitle_processor
```

### 2. 下载 FFmpeg

由于 FFmpeg 文件过大（超过 GitHub 100MB 限制），请单独下载：

1. 访问 https://www.gyunwa.com/2024/ffmpeg.html 或 https://www.gyang.com/ffmpeg.html
2. 下载 `ffmpeg-latest.7z` 或 `ffmpeg-master-latest-win64-gpl.zip`
3. 解压后，将 `ffmpeg.exe`、`ffprobe.exe`、`ffplay.exe` 复制到项目根目录的 `ffmpeg/` 文件夹

### 3. 安装 PaddleOCR GPU 环境

```bash
# 创建虚拟环境
python -m venv paddleocr_env
paddleocr_env\Scripts\activate

# 安装依赖
pip install paddlepaddle-gpu paddleocr PyQt5 requests
```

### 4. 安装 Ollama 并下载翻译模型

```bash
# 安装 Ollama: https://ollama.ai

# 下载翻译模型
ollama pull quantumcookie/sakura-galtransl-v3.7:7b
```

### 5. 配置

```bash
# 复制配置模板
copy config\config.example.json config\config.json

# 编辑 config.json，设置 PaddleOCR 环境路径
```

### 6. 运行程序

```bash
# 编辑 run.bat，设置正确的路径
run.bat
```

## 项目结构

```
AVT_subtitle_processor/
├── main.py                 # 程序入口
├── run.bat                 # 启动脚本
├── requirements.txt        # 依赖列表
├── ffmpeg/                 # FFmpeg 工具（需单独下载）
├── modules/
│   ├── config_manager.py   # 配置管理
│   ├── video_manager.py    # 视频管理
│   ├── subtitle_engine.py  # 字幕处理引擎
│   ├── main_window.py      # 主窗口
│   ├── config_panel.py     # 配置面板
│   ├── progress_panel.py   # 进度面板
│   ├── log_viewer.py       # 日志查看器
│   └── translator.py       # 翻译模块
├── config/
│   └── config.example.json # 配置模板
└── videos/                 # 视频输入目录
```

## 使用说明

1. **添加视频**: 点击"添加视频"按钮或拖拽视频文件到列表
2. **配置参数**: 在右侧配置面板调整 OCR、翻译、烧录参数
3. **开始处理**: 点击"开始处理"按钮
4. **查看进度**: 底部进度条和日志窗口显示实时状态

## 配置说明

### OCR 配置
- **检测阈值**: 控制字幕检测灵敏度
- **识别置信度**: 过滤低质量识别结果
- **帧间隔**: 每隔多少秒提取一帧

### 翻译配置
- **超时时间**: 单条字幕翻译超时
- **重试次数**: 翻译失败重试次数
- **温度参数**: 控制翻译随机性

### 烧录配置
- **编码预设**: NVENC 编码速度/质量平衡
- **质量因子**: CRF 值，越低质量越好
- **字体大小**: 字幕显示大小

## 许可证

MIT License

## 版本历史

### v1.0.0 (2025-05-10)
- 初始版本发布
- 支持日语字幕提取、翻译、烧录
- PyQt5 图形界面
- 批量处理功能
- 断点续传功能

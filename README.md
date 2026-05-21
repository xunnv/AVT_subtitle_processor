# AVT字幕处理器

<div align="center">

![AVT Logo](https://via.placeholder.com/128x128?text=AVT)

**基于 PyQt5 的全自动日语视频字幕提取、翻译与烧录工具**


**项目地址：https://github.com/xunnv/AVT_subtitle_processor**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows-0078d7.svg)](https://www.microsoft.com/windows)

</div>

---

## 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [系统要求](#系统要求)
- [安装指南](#安装指南)
- [使用说明](#使用说明)
- [配置说明](#配置说明)
- [项目结构](#项目结构)
- [开发指南](#开发指南)
- [常见问题](#常见问题)
- [许可证](#许可证)

---

## 项目简介

AVT 字幕处理器（Auto Video Translation）是一个功能强大的 Windows 桌面应用程序，专门用于日语视频的字幕提取、翻译和烧录。该程序集成了 PaddleOCR GPU 自动识别、Ollama 本地模型翻译以及 NVENC 硬件加速烧录，实现了从视频到最终字幕文件的全自动化处理流程。

### 核心亮点

- 🚀 **全流程自动化** - 一键完成字幕提取、翻译、烧录
- 🔍 **高精度识别** - 基于 PaddleOCR GPU 实现准确的日语文本检测
- 🌐 **本地翻译** - 使用 Ollama 本地模型，无需联网即可翻译
- ⚡ **高性能处理** - NVENC GPU 硬件加速编码
- 📊 **实时监控** - 详细的进度显示和日志记录
- 🔄 **断点续传** - 智能检测已完成步骤，支持从断点继续

---

## 功能特性

### 字幕提取
- 基于 PaddleOCR GPU 的高准确率日语字幕识别
- 支持自定义帧间隔，平衡处理速度与识别精度
- 智能区域检测，聚焦字幕区域
- 文本去重和合并，避免重复字幕

### 翻译系统
- 支持 Ollama 和 LM Studio 双翻译框架
- 批量异步翻译，大幅提升翻译效率
- 自定义翻译模型配置
- 自动重试机制，保证翻译成功率

### 字幕烧录
- NVENC GPU 硬件加速编码
- 高质量 ASS 字幕渲染
- 自定义字幕样式（字体、颜色、大小）
- 批量烧录处理

### 用户体验
- 现代化的深色主题界面
- 实时进度条和状态显示
- 完整的日志记录系统
- 支持视频拖拽添加
- 多视频队列批量处理

---

## 技术栈

| 组件 | 技术 | 版本要求 |
|------|------|---------|
| GUI 框架 | PyQt5 | ≥5.15.10 |
| OCR 引擎 | PaddleOCR | ≥2.8.1 |
| 深度学习框架 | PaddlePaddle GPU | ≥2.6.2 |
| 翻译框架 | Ollama / LM Studio | 最新版 |
| 视频处理 | FFmpeg | ≥6.0 |
| 异步请求 | aiohttp | ≥3.13.0 |
| 打包工具 | PyInstaller | ≥6.3.0 |

---

## 系统要求

### 最低配置
- **操作系统**: Windows 10 64位 或更高
- **处理器**: Intel i5 或 AMD 同等性能
- **内存**: 8GB RAM
- **显卡**: NVIDIA 显卡（支持 CUDA 11.x）
- **存储**: 10GB 可用空间

### 推荐配置
- **操作系统**: Windows 11 64位
- **处理器**: Intel i7 或 AMD Ryzen 7
- **内存**: 16GB+ RAM
- **显卡**: NVIDIA RTX 3060 或更高
- **存储**: 20GB+ SSD 可用空间

---

## 安装指南

### 1. 获取源码

```bash
git clone https://github.com/XUNNV/AVT_subtitle_processor.git
cd AVT_subtitle_processor
```

### 2. 创建并激活虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate
```

### 3. 安装依赖

```bash
# 安装 PyPI 依赖
pip install -r requirements.txt
```

### 4. 配置 PaddleOCR 环境

#### 方案一：使用独立虚拟环境（推荐）

```bash
# 创建 PaddleOCR 专用虚拟环境
python -m venv paddleocr_env
paddleocr_env\Scripts\activate

# 安装 PaddleOCR 依赖
pip install paddlepaddle-gpu paddleocr

# 在 AVT 配置中设置 PADDLEOCR_VENV 环境变量
# 或在 config.json 中配置 paths.python_path
```

#### 方案二：与主程序共用环境

```bash
# 在主虚拟环境中安装
pip install paddlepaddle-gpu paddleocr
```

### 5. 准备 FFmpeg

```bash
# 方法一：将 FFmpeg 放入项目 bin 目录
# 下载 FFmpeg: https://github.com/BtbN/FFmpeg-Builds/releases
# 解压后将 ffmpeg.exe 和 ffprobe.exe 放入 bin/ 目录

# 方法二：使用系统已安装的 FFmpeg
# 在 config.json 中配置 paths.ffmpeg_path 和 paths.ffprobe_path
```

### 6. 安装 Ollama（或 LM Studio）

#### Ollama 配置

```bash
# 下载并安装 Ollama: https://ollama.ai/download

# 启动 Ollama 服务
ollama serve

# 下载翻译模型
ollama pull quantumcookie/sakura-galtransl-v3.7:7b
```

#### LM Studio 配置（可选）

```bash
# 下载 LM Studio: https://lmstudio.ai
# 下载 Sakura 系列模型
# 在配置中选择 LM Studio 翻译框架
```

### 7. 配置程序

```bash
# 复制配置模板
copy config\config.example.json config\config.json

# 编辑 config.json，根据需要调整配置
```

### 8. 运行程序

```bash
# 方法一：使用 Python 直接运行
python main.py

# 方法二：使用启动脚本
run.bat

# 方法三：使用 VBS 脚本隐藏控制台
启动.vbs
```

---

## 使用说明

### 快速开始

1. **添加视频**
   - 点击「添加视频」按钮选择视频文件
   - 或直接拖拽视频文件到视频列表
   - 支持 MP4、MKV、AVI、MOV 等常见格式

2. **配置参数**
   - 在右侧配置面板调整各项参数
   - 确认翻译框架和模型已正确配置

3. **开始处理**
   - 点击「开始处理」按钮
   - 底部进度条和日志显示实时状态

4. **查看结果**
   - 处理完成后视频保存在 output/videos/
   - 字幕文件保存在 output/subtitles/

### 详细使用

#### OCR 参数配置
- **检测阈值** (0.1-1.0): 控制字幕检测灵敏度
- **识别置信度** (0.1-1.0): 过滤低质量识别结果
- **帧间隔** (秒): 每隔多少秒提取一帧
- **启用 GPU**: 推荐开启，大幅提升识别速度

#### 翻译参数配置
- **翻译框架**: 选择 Ollama 或 LM Studio
- **主机地址**: 本地模型服务地址
- **模型名称**: 使用的翻译模型
- **超时时间** (秒): 单条字幕翻译超时
- **最大重试**: 翻译失败重试次数
- **温度参数** (0.0-1.0): 控制翻译随机性

#### 字幕样式配置
- **字体名称**: 字幕使用的字体
- **字体大小**: 字幕文字大小
- **主色**: 字幕主要颜色
- **描边颜色**: 字幕描边颜色
- **描边宽度**: 字幕描边粗细
- **垂直边距**: 字幕距离底部距离

---

## 配置说明

完整配置文件位于 `config/config.json`，包含以下主要部分：

### 路径配置
```json
{
  "paths": {
    "video_input": "./videos",
    "output_dir": "./output",
    "ffmpeg_path": "ffmpeg",
    "ffprobe_path": "ffprobe",
    "python_path": ""
  }
}
```

### OCR 配置
```json
{
  "ocr": {
    "lang": "japan",
    "use_gpu": true,
    "enable_mkldnn": false,
    "det_db_thresh": 0.3,
    "det_db_box_thresh": 0.5,
    "rec_score_thresh": 0.5,
    "frame_interval": 1,
    "frame_quality": 2
  }
}
```

### 翻译配置
```json
{
  "translation": {
    "framework": "ollama",
    "ollama": {
      "host": "http://localhost:11434",
      "model": "quantumcookie/sakura-galtransl-v3.7:7b",
      "timeout": 120,
      "max_retries": 3,
      "temperature": 0.3
    }
  }
}
```

### 烧录配置
```json
{
  "burn": {
    "preset": "p4",
    "crf": 23
  }
}
```

### 处理配置
```json
{
  "processing": {
    "auto_skip_processed": true,
    "wait_between_videos": 60,
    "cleanup_temp": true,
    "temp_dir": ""
  }
}
```

---

## 项目结构

```
AVT_subtitle_processor/
├── main.py                      # 程序入口
├── requirements.txt             # 项目依赖
├── run.bat                      # 启动脚本（Windows）
├── build.bat                    # 打包脚本
├── clean.bat                    # 清理脚本
├── 启动.vbs                     # 隐藏控制台启动
│
├── bin/                         # FFmpeg 工具目录
│   ├── ffmpeg.exe
│   ├── ffprobe.exe
│   └── README.md
│
├── config/                      # 配置文件目录
│   ├── config.example.json      # 配置模板
│   └── config.json              # 用户配置（不提交）
│
├── modules/                     # 核心模块
│   ├── __init__.py
│   ├── config_manager.py        # 配置管理
│   ├── video_manager.py         # 视频管理
│   ├── subtitle_engine.py       # 字幕处理引擎
│   ├── translator.py            # 翻译模块
│   ├── logger.py                # 日志系统
│   ├── security.py              # 安全工具
│   ├── ffmpeg_utils.py          # FFmpeg 工具
│   ├── main_window.py           # 主窗口
│   ├── config_panel.py          # 配置面板
│   ├── progress_panel.py        # 进度面板
│   └── log_viewer.py            # 日志查看器
│
├── tests/                       # 单元测试
│   ├── test_config_manager.py
│   └── test_security.py
│
├── videos/                      # 视频输入目录
│   └── README.txt
│
├── output/                      # 输出目录（自动生成）
│   ├── videos/                  # 处理后的视频
│   ├── subtitles/               # 字幕文件
│   └── work_*/                  # 临时工作目录
│
├── logs/                        # 日志目录（自动生成）
│   └── avt.log
│
├── .gitignore                   # Git 忽略文件
├── README.md                    # 项目说明
├── LICENSE                      # 许可证
├── CONTRIBUTING.md              # 贡献指南
└── docs/                        # 文档目录
    ├── PaddleOCR_使用教程.md
    ├── FFMPEG打包准备.md
    └── 外部依赖说明.md
```

---

## 开发指南

### 环境搭建

```bash
# 1. 克隆项目
git clone https://github.com/XUNNV/AVT_subtitle_processor.git
cd AVT_subtitle_processor

# 2. 创建开发环境
python -m venv venv
venv\Scripts\activate

# 3. 安装开发依赖
pip install -r requirements.txt
pip install black flake8 pytest

# 4. 运行测试
pytest tests/ -v
```

### 代码规范

项目遵循以下编码规范：
- **PEP 8** - Python 代码风格
- **类型注解** - 使用类型提示
- **文档字符串** - 使用 Google 风格
- **Git 分支** - 使用 Git Flow 工作流

### 提交代码

```bash
# 1. 创建功能分支
git checkout -b feature/your-feature

# 2. 提交更改
git add .
git commit -m "feat: 描述你的更改"

# 3. 推送到远程
git push origin feature/your-feature

# 4. 创建 Pull Request
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_config_manager.py -v

# 查看覆盖率
pytest --cov=modules tests/
```

---

## 常见问题

### Q: OCR 识别效果不佳怎么办？
**A**: 
- 提高检测阈值 (`det_db_thresh`)
- 调整帧间隔，更多帧可能提高准确性
- 确保视频质量良好，字幕清晰
- 尝试调整 `rec_score_thresh` 过滤低质量结果

### Q: 翻译速度很慢？
**A**:
- 检查是否使用 GPU 进行翻译
- 调整超时时间和重试次数
- 考虑使用更轻量的模型

### Q: 字幕烧录失败？
**A**:
- 检查 FFmpeg 路径配置是否正确
- 查看日志中的详细错误信息
- 确保输出目录有写权限
- 尝试降低编码质量参数

### Q: 如何查看详细日志？
**A**:
- 程序界面底部有日志查看器
- 日志文件保存在 `logs/avt.log`
- 可以调整日志级别获取更详细信息

### Q: 程序可以在没有 GPU 的电脑上运行吗？
**A**:
- 可以，但需要修改配置使用 CPU 版本的 PaddlePaddle
- 处理速度会较慢
- 字幕烧录可能无法使用硬件加速

更多常见问题请参考 [FAQ.md](docs/FAQ.md)。

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 致谢

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 强大的 OCR 引擎
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - Python GUI 框架
- [Ollama](https://ollama.ai) - 本地大语言模型服务
- [FFmpeg](https://ffmpeg.org) - 强大的多媒体处理工具
- [Sakura](https://github.com/SakuraLLM) - 优秀的翻译模型系列

---

## 贡献

我们欢迎任何形式的贡献！请先阅读 [贡献指南](CONTRIBUTING.md)。

---

## 版本历史

### v1.0.0 (2025-05-10)
- ✨ 初始版本发布
- 📝 支持日语字幕提取、翻译、烧录
- 🖥️ PyQt5 图形界面
- 📋 批量处理功能
- 🔄 断点续传功能
- 📊 增强日志系统
- 🔒 添加路径安全校验
- ⚡ OCR 引擎单例化优化
- 🌐 异步批量翻译功能

---

<div align="center">

**Made with ❤️ by XUNNV**

</div>

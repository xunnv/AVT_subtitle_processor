# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

### Removed

## [1.0.0] - 2025-05-21

### Added

- ✨ 初始版本发布
- 📝 基于 PyQt5 的图形界面
- 🔍 集成 PaddleOCR GPU 进行日语字幕识别
- 🌐 支持 Ollama 和 LM Studio 双翻译框架
- ⚡ NVENC GPU 硬件加速字幕烧录
- 📊 实时进度显示和日志系统
- 🔄 智能断点续传功能
- 📋 多视频队列批量处理
- 🎨 自定义字幕样式配置
- 🔒 路径安全校验功能
- 📁 完整的配置管理系统

### Changed

- OCR 引擎采用单例模式优化性能
- 翻译模块支持异步批量处理
- 增强日志系统，支持多种日志级别

### Fixed

- 修复打包后 FFmpeg 路径问题
- 修复 Cython Utility 目录缺失问题
- 修复 imageio 元数据缺失问题
- 修复 Qt 高 DPI 缩放警告

### Removed

- 无

## [1.0.0-beta] - 2025-05-10

### Added

- 基础 OCR 字幕提取功能
- 基础翻译功能
- 基础字幕烧录功能
- 简单的命令行界面

[Unreleased]: https://github.com/XUNNV/AVT_subtitle_processor/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/XUNNV/AVT_subtitle_processor/releases/tag/v1.0.0
[1.0.0-beta]: https://github.com/XUNNV/AVT_subtitle_processor/releases/tag/v1.0.0-beta

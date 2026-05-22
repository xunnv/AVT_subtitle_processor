# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-05-22

### Fixed

- 修复打包后 FFmpeg 路径解析错误：`get_base_dir()` 在 frozen 环境使用 `sys._MEIPASS` 替代 `os.path.dirname(sys.executable)`
- 修复 `ModuleNotFoundError: No module named 'unittest'`：通过 post-COLLECT 从 `sys.base_prefix/Lib` 复制 unittest 模块
- 修复 `FileNotFoundError: Cython/Utility/CppSupport.cpp`：通过 post-COLLECT 从 venv 复制 Cython/Utility 目录
- 修复 `paddle/` 子目录缺失（仅 2 个而非 42 个）：post-COLLECT 从 venv 补充全部子目录
- 修复 `paddleocr/` 目录缺失：post-COLLECT 从 venv 完整复制
- 修复 `bin/ffmpeg.exe` 被 COLLECT 创建为目录导致 `[WinError 5] 拒绝访问`：spec 中移除 `a.datas.append()` 并改用 post-COLLECT 文件复制
- 修复 `a.datas` 参数在 PyInstaller 中完全失效的问题：所有模块改用 post-COLLECT 文件复制
- 修复 spec 中 `PROJECT_ROOT` 计算错误（`SPECPATH` 在 PyInstaller 中已是目录非文件）
- 修复 `opencv2` 和 `python_docx` 隐藏导入名称错误

### Changed

- FFmpeg 路径由绝对路径统一改为相对路径（`./bin/ffmpeg.exe`）
- `_resolve_tool_path()` 增加三级降级路径查找（`_meipass` → `base_dir` → `base_dir/_internal`）
- `.spec` 文件增加完整 post-COLLECT 复制逻辑处理被 PyInstaller 硬编码排除的模块
- `requirements.txt` 从 7 行扩展为 40+ 个完整依赖，标注最低版本
- `.gitignore` 不再排除 `*.spec`（打包配置文件需版本控制）
- `README.md` 更新路径配置和项目结构

### Added

- `docs/打包指南.md`：标准化可复用打包文档，含完整步骤、验证清单、故障排查指南
- `docs/FFMPEG打包准备.md`：重写，修正 `_internal/` 路径说明
- `docs/外部依赖说明.md`：重写，区分用户端/开发者端，修正 CUDA 版本和 FFmpeg 路径
- `docs/Cython异常排查指南.md`：更新，加入 post-COLLECT 方案和 unittest 错误码
- `build.bat` 第三步验证逻辑
- `.spec` 新增 post-COLLECT 步骤 10：统一清理 `__pycache__/` 和 `.pyc/.pyo` 缓存文件
- 打包验证清单新增缓存洁净性检查

### Removed

- 删除 `docs/打包计划.md`（已被 `打包指南.md` 取代，命令行参数方式在实际打包中无效）
- 清理项目 `modules/__pycache__/`、`tests/__pycache__/` 及 dist 残留缓存

## [1.0.0] - 2026-05-21

### Added

- 初始版本发布
- 基于 PyQt5 的图形界面
- 集成 PaddleOCR GPU 进行日语字幕识别
- 支持 Ollama 和 LM Studio 双翻译框架
- NVENC GPU 硬件加速字幕烧录
- 实时进度显示和日志系统
- 智能断点续传功能
- 多视频队列批量处理
- 自定义字幕样式配置
- 路径安全校验功能
- 完整的配置管理系统

### Changed

- OCR 引擎采用单例模式优化性能
- 翻译模块支持异步批量处理
- 增强日志系统，支持多种日志级别

## [1.0.0-beta] - 2026-05-10

### Added

- 基础 OCR 字幕提取功能
- 基础翻译功能
- 基础字幕烧录功能
- 简单的命令行界面
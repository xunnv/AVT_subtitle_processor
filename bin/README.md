# FFmpeg 放置位置

本目录用于存放 FFmpeg 二进制文件。

> **注意**：打包后 FFmpeg 位于 `_internal/bin/`（PyInstaller onedir 模式），而非 exe 同级目录。程序通过 `_resolve_tool_path()` 自动定位。

## 需放置的文件

- `bin/ffmpeg.exe` (~97 MB)
- `bin/ffprobe.exe` (~97 MB)

## 下载地址

https://www.gyan.dev/ffmpeg/builds/

推荐下载：`ffmpeg-git-essentials.7z`（仅必需文件）或 `ffmpeg-git-full.7z`（完整版）

## Git 管理

这两个文件因体积过大不提交至版本控制（已加入 `.gitignore`）。建议在 `docs/FFMPEG打包准备.md` 中为其他开发者记录下载步骤。
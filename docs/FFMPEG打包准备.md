# FFmpeg 打包说明

> FFmpeg 的打包已通过 `.spec` 文件的 **post-COLLECT** 阶段自动处理，详见 [打包指南](打包指南.md)。

## 快速回顾

### 1. 项目 bin/ 目录

确保 FFmpeg 二进制文件位于项目 `bin/` 目录：

```
avt_subtitle_processor/
└── bin/
    ├── ffmpeg.exe      (~97 MB)
    └── ffprobe.exe     (~97 MB)
```

### 2. 下载地址

- 推荐：https://www.gyan.dev/ffmpeg/builds/
- 下载 `ffmpeg-git-essentials.7z` 或 `ffmpeg-git-full.7z`
- 解压后将 `bin/ffmpeg.exe` 和 `bin/ffprobe.exe` 复制到项目 `bin/`

### 3. 打包后位置

打包后 FFmpeg 位于：

```
dist/AVT_Subtitle_Processor/_internal/bin/
├── ffmpeg.exe
└── ffprobe.exe
```

程序通过 `_resolve_tool_path()` 自动定位到此路径，无需手动配置。

### 4. .gitignore

FFmpeg 二进制文件已加入 `.gitignore`（体积过大，不提交版本控制）：

```gitignore
bin/ffmpeg.exe
bin/ffprobe.exe
```

打包时 `.spec` 的 post-COLLECT 步骤会自动从项目 `bin/` 复制到 dist。

---

> **注意**：本文档仅作为 FFmpeg 打包的背景说明。完整的打包流程和验证清单请查阅 [打包指南](打包指南.md)。
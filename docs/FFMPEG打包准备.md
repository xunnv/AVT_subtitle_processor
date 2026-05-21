# FFmpeg 打包准备说明

## 📝 操作步骤

### 1. 创建 bin 目录

在项目根目录创建 `bin` 文件夹：
```
avt_subtitle_processor/
└── bin/
```

### 2. 下载 FFmpeg

从以下地址下载 FFmpeg：
- 官方：https://www.gyan.dev/ffmpeg/builds/
- 推荐：下载 `ffmpeg-git-full.7z`（最新完整版）

### 3. 解压并放置文件

解压下载的压缩包，找到以下文件并放到 `bin/` 目录：
```
bin/
├── ffmpeg.exe
└── ffprobe.exe
```

### 4. 检查 spec 文件

确认 `AVT_Subtitle_Processor.spec` 文件中已经包含了对 `bin` 目录的收集：
```python
datas += [
    ('config', 'config'),
    ('bin', 'bin'),
]
```

### 5. 正常打包

运行打包脚本，FFmpeg 会自动包含在输出中！

---

## 📦 打包后的目录结构

用户得到的分发包将是：
```
AVT_Subtitle_Processor/
├── AVT_Subtitle_Processor.exe
├── bin/              ← FFmpeg 自动打包在这里
│   ├── ffmpeg.exe
│   └── ffprobe.exe
├── config/
│   └── config.json
└── _internal/
```

程序会自动从 `bin/` 目录读取 FFmpeg，用户无需手动配置！

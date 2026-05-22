# 贡献指南

感谢您对 AVT 字幕处理器项目的关注！我们欢迎各种形式的贡献。

---

## 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [打包说明](#打包说明)
- [提交规范](#提交规范)
- [问题反馈](#问题反馈)

---

## 行为准则

### 我们的承诺

为了营造开放和友好的环境，我们承诺：

- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 不可接受的行为

- 使用性化的语言或图像
- 恶意评论或人身攻击
- 公开或私下骚扰
- 未经许可发布他人的私人信息
- 其他不专业或不恰当的行为

---

## 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请使用 GitHub Issues：

1. 先搜索是否已有相关 Issue
2. 使用 Issue 模板创建新 Issue
3. 提供详细的复现步骤
4. 附上相关截图或日志

### 提交代码

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/your-feature`)
3. 提交您的更改
4. 推送到分支 (`git push origin feature/your-feature`)
5. 创建 Pull Request

---

## 开发流程

### 环境设置

```bash
# 1. Fork 并克隆
git clone https://github.com/your-username/AVT_subtitle_processor.git
cd AVT_subtitle_processor

# 2. 创建虚拟环境（Python 3.12+）
python -m venv venv
venv\Scripts\activate

# 3. 安装开发依赖
pip install -r requirements.txt
pip install black flake8 pytest mypy

# 4. 安装 pre-commit hooks（可选但推荐）
pip install pre-commit
pre-commit install

# 5. 放置 FFmpeg 二进制文件
# 从 https://www.gyan.dev/ffmpeg/builds/ 下载并将 ffmpeg.exe 和 ffprobe.exe 放入 bin/
```

### 代码规范

#### Python 代码

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 代码风格
- 使用类型注解
- 使用 Google 风格的文档字符串
- 函数和方法需要 docstring

#### 格式化工具

```bash
# 使用 black 格式化
black modules/ tests/

# 使用 flake8 检查
flake8 modules/ tests/
```

#### 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_config_manager.py -v
```

---

## 打包说明

### 打包流程

本项目使用 PyInstaller 打包，完整流程请查阅 [docs/打包指南.md](docs/打包指南.md)。

关键命令：

```powershell
# 清理旧产物
Remove-Item -Recurse -Force dist, build

# 使用 .spec 文件打包
pyinstaller AVT_Subtitle_Processor.spec --clean --noconfirm

# 或使用一键脚本
.\build.bat
```

### 打包注意事项

以下模块因 PyInstaller 硬编码排除，`.spec` 通过 post-COLLECT 步骤处理：

- `unittest` — Paddle cpp_extension 依赖
- `Cython/Utility/` — Cython C++ 模板文件
- `paddleocr/`, `paddle/` — 模块完整性补充
- `imgaug/`, `docx/`, `imageio/` — 数据文件模块

---

## 提交规范

### 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例

```
feat(ocr): 添加 OCR 引擎单例化优化

- 实现 OCR 引擎延迟初始化
- 提升批量处理性能
- 添加相关单元测试

Closes #123
```

---

## Pull Request 流程

### 提交前检查清单

- [ ] 代码通过所有测试
- [ ] 代码符合项目规范
- [ ] 已添加必要的文档
- [ ] Commit 信息格式正确
- [ ] 更新了 CHANGELOG.md（如需要）
- [ ] 验证 spec 打包仍能正常执行

### 审查流程

1. 创建 PR 后，维护者会进行代码审查
2. 根据审查意见进行修改
3. 至少一位维护者批准后合并

---

## 问题反馈

### Bug 报告模板

```markdown
**描述问题：**
简短描述你遇到的问题

**复现步骤：**
1. 步骤 1
2. 步骤 2
3. 步骤 3

**预期行为：**
描述你期望发生的事情

**实际行为：**
描述实际发生的事情

**环境信息：**
- 操作系统：Windows 10/11
- Python 版本：
- 程序版本：
- 相关配置：

**日志/截图：**
如果有相关日志或截图请附上
```

### 功能请求模板

```markdown
**功能描述：**
简短描述你想要的功能

**问题背景：**
这个功能解决了什么问题

**解决方案：**
你希望的解决方案是什么

**替代方案：**
有没有考虑过其他替代方案

**额外说明：**
其他相关信息
```

---

## 许可证

通过贡献代码，您同意您的贡献将根据 MIT 许可证发布。

---

再次感谢您的贡献！
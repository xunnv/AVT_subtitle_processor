# Cython/Utility/CppSupport.cpp 异常排查指南

## 问题描述

程序运行时出现与 `Cython/Utility/CppSupport.cpp` 相关的异常，通常表现为：
- 程序启动时崩溃
- 显示找不到 C++ 相关的 DLL 加载失败
- 与 Cython 编译的模块无法加载

## 可能原因

### 1. Microsoft Visual C++ Redistributable 未安装

**这是最常见的原因！**

| 组件 | 说明 |
|------|------|
| **VC++ 2015-2022 Redistributable (x64) | 必须安装 |

### 2. PyInstaller 打包时缺少隐藏导入

某些 Cython 编译的模块没有被正确打包

### 3. 缺少必要的 C++ 运行时 DLL 缺失

`vcruntime140.dll`、`msvcp140.dll 等文件缺失

### 4. 路径问题

程序尝试访问源代码路径而非打包后的路径

## 解决方案

### 方案一：安装 VC++ 运行时库（推荐先试）

下载安装：https://aka.ms/vs/17/release/vc_redist.x64.exe

### 方案二：使用优化的打包配置

使用 `AVT_Subtitle_Processor.spec` 文件重新打包：

```bash
pyinstaller AVT_Subtitle_Processor.spec
```

该 `.spec` 文件包含了：
- 完整的隐藏导入
- 数据文件收集
- Cython 相关模块
- 所有依赖自动检查

### 方案三：程序内置检查

程序已内置运行时检查，缺少 VC++ 运行时会提示用户

## 验证步骤

### 1. 检查 VC++ 运行时

打开命令提示符，运行：

```cmd
where vcruntime140.dll
```

如果找不到，需要安装 VC++ Redistributable

### 2. 查看完整错误信息

如果程序显示错误，查看 `logs/avt.log` 文件，会有更详细的堆栈跟踪

### 3. 使用 spec 文件重新打包

```bash
# 1. 删除旧的打包文件
Remove-Item -Recurse -Force dist, build

# 2. 使用 spec 文件重新打包
pyinstaller AVT_Subtitle_Processor.spec
```

## 预防措施

### 开发者预防

1. **使用 spec 文件而非命令行参数
2. **在程序中加入运行时检查
3. **在 README 中明确说明 VC++ 依赖
4. **将 VC++ 运行时下载链接放在 README

### 用户端

1. **运行程序前，检查 VC++ 运行时（程序会提示
2. **使用管理员权限安装 VC++ Redistributable
3. **重启电脑后再尝试运行程序

## 常见错误代码

| 错误代码 | 可能原因 |
|---------|---------|
| `ImportError: DLL load failed` | VC++ 运行时缺失 |
| `ModuleNotFoundError: No module named 'cython'` | 缺少隐藏导入 |
| `FileNotFoundError: ...CppSupport.cpp` | 尝试访问源代码路径 |

## 补充 DLL 列表

确保以下 DLL 在用户电脑上存在：

- `vcruntime140.dll`
- `vcruntime140_1.dll`
- `msvcp140.dll`
- `msvcp140_1.dll`
- `msvcp140_2.dll`

## 联系支持

如果以上都解决，请：
1. 查看日志文件 `logs/avt.log`
2. 检查用户的 Windows 版本
3. 确认为 64 位系统

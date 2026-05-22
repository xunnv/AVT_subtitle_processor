# Cython/Utility/CppSupport.cpp 异常排查指南

## 问题描述

程序运行时出现与 `Cython/Utility/CppSupport.cpp` 相关的异常，通常表现为：

- 程序启动时崩溃
- `FileNotFoundError: ...Cython\Utility\CppSupport.cpp`
- 与 Cython 编译的模块无法加载

## 常见原因

### 1. Microsoft Visual C++ Redistributable 未安装

**最常见的原因。** 需安装 VC++ 2015-2022 Redistributable (x64)：

```
下载地址：https://aka.ms/vs/17/release/vc_redist.x64.exe
```

程序启动时会自动检测并提示安装。

### 2. 打包后 Cython/Utility 目录缺失

PyInstaller 不会自动收集 Cython 的非 Python 数据文件（.cpp、.h 等 C++ 模板）。

**打包解决方案**：已通过 `.spec` 文件的 post-COLLECT 阶段从 venv 完整复制 `Cython/Utility/` 目录。详见 [打包指南](打包指南.md)。

## 解决方案

### 用户端

1. 确保已安装 VC++ 2015-2022 Redistributable (x64)
2. 查看日志 `logs/avt.log` 获取详细错误信息
3. 确认为 64 位 Windows 系统

### 开发者端

使用 `.spec` 文件打包（已包含 Cython/Utility 复制逻辑）：

```powershell
pyinstaller AVT_Subtitle_Processor.spec --clean --noconfirm
```

## 验证步骤

```cmd
# 检查 VC++ 运行时是否存在
where vcruntime140.dll
```

## 常见错误码

| 错误 | 原因 |
|---|---|
| `ImportError: DLL load failed` | VC++ 运行时缺失 |
| `FileNotFoundError: ...CppSupport.cpp` | Cython/Utility 未打包 |
| `ModuleNotFoundError: No module named 'unittest'` | unittest 模块未打包 |

## 必需 DLL

- `vcruntime140.dll`
- `vcruntime140_1.dll`
- `msvcp140.dll`
- `msvcp140_1.dll`
- `msvcp140_2.dll`

---
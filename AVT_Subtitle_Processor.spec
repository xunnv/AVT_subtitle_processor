# -*- mode: python ; coding: utf-8 -*-
"""
AVT_Subtitle_Processor.spec
PyInstaller 打包配置文件 - PaddleOCR GPU 版本

基于老版本已验证的模块依赖配置，增强以下方面：
  - 完整的 PaddleOCR/paddle 子模块自动收集
  - NVIDIA CUDA 运行时 DLL 自动收集
  - 隐藏导入（importlib 动态加载的模块）
  - 相对路径支持（ffmpeg/bin 目录）
"""

import os
import sys
from pathlib import Path

# ============================================================
# 项目路径配置
# ============================================================
PROJECT_ROOT = os.path.abspath(SPECPATH)  # SPECPATH 即为项目根目录
PROJECT_SRC = PROJECT_ROOT  # main.py 所在目录

# ============================================================
# 隐藏导入列表（PaddleOCR 及动态加载的依赖）
# ============================================================
HIDDEN_IMPORTS = [
    # --- PaddleOCR 核心 ---
    'paddleocr',
    'paddleocr.paddleocr',
    'paddleocr.ppocr',
    'paddleocr.ppocr.postprocess',
    'paddleocr.ppocr.data',
    'paddleocr.ppocr.data.imaug',
    'paddleocr.ppocr.utils',
    'paddleocr.ppstructure',
    'paddleocr.tools',
    'paddleocr.tools.infer',
    'paddleocr.tools.infer.utility',
    'paddleocr.tools.infer.predict_det',
    'paddleocr.tools.infer.predict_rec',
    'paddleocr.tools.infer.predict_cls',
    'paddleocr.tools.infer.predict_system',
    'paddleocr.tools.infer.predict_e2e',
    'paddleocr.tools.infer.predict_sr',

    # --- PaddlePaddle 核心 ---
    'paddle',
    'paddle._C_ops',
    'paddle._C',
    'paddle._legacy_C_ops',
    'paddle._pir_ops',
    'paddle.base',
    'paddle.base.core',
    'paddle.base.proto',
    'paddle.base.proto.framework_pb2',
    'paddle.framework',
    'paddle.framework.framework',
    'paddle.distributed',
    'paddle.cuda',
    'paddle.io',
    'paddle.io.dataloader',
    'paddle.static',
    'paddle.static.nn',
    'paddle.nn',
    'paddle.nn.functional',
    'paddle.nn.layer',
    'paddle.nn.utils',
    'paddle.vision',
    'paddle.vision.models',
    'paddle.vision.transforms',
    'paddle.vision.datasets',
    'paddle.utils',
    'paddle.utils.download',
    'paddle.utils.cpp_extension',
    'paddle.utils.cpp_extension.extension_utils',
    'paddle.geometric',
    'paddle.geometric.message_passing',
    'paddle.incubate',
    'paddle.distribution',
    'paddle.quantization',
    'paddle.compat',
    'paddle.jit',

    # --- PaddleOCR 依赖库 ---
    'pyclipper',
    'shapely',
    'shapely.geometry',
    'lmdb',
    'skimage',
    'skimage.draw',
    'skimage.filters',
    'skimage.morphology',
    'skimage.measure',
    'skimage.io',
    'skimage.exposure',
    'skimage.transform',
    'skimage.color',
    'imgaug',
    'imgaug.augmenters',
    'cv2',  # opencv-python
    'PIL',
    'PIL.Image',
    'numpy',
    'numpy.core',
    'numpy.linalg',
    'scipy',
    'scipy.special',
    'scipy.ndimage',
    'scipy.interpolate',
    'matplotlib',
    'matplotlib.pyplot',
    'lxml',
    'lxml.etree',

    # --- 项目依赖 ---
    'PyQt5',
    'PyQt5.QtWidgets',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtNetwork',
    'requests',
    'aiohttp',
    'certifi',
    'charset_normalizer',
    'chardet',
    'ujson',
    'multidict',
    'yaml',

    # --- 老版本原有的额外依赖 ---
    'docx',                # python-docx
    'imageio',             # imageio (paddleocr/skimage 依赖)
    'imageio.core',
    'imageio.plugins',

    # --- 标准库模块（PyInstaller 默认排除但 Paddle 运行时需要）---
    'unittest',
    'unittest.mock',

    # --- Cython 运行时支持（防止 Cython/Utility/CppSupport.cpp 异常）---
    'Cython',
    'Cython.Compiler',
    'Cython.Plex',
    'Cython.Utility',
]

# ============================================================
# 数据文件收集
# ============================================================
DATAS = []

# config 目录 — 逐个添加文件确保被收集
config_dir = os.path.join(PROJECT_ROOT, 'config')
if os.path.isdir(config_dir):
    for fname in os.listdir(config_dir):
        fpath = os.path.join(config_dir, fname)
        if os.path.isfile(fpath):
            DATAS.append((fpath, os.path.join('config', fname)))

# bin 目录（FFmpeg）— 逐个添加文件确保被收集
bin_dir = os.path.join(PROJECT_ROOT, 'bin')
if os.path.isdir(bin_dir):
    for fname in os.listdir(bin_dir):
        fpath = os.path.join(bin_dir, fname)
        if os.path.isfile(fpath):
            DATAS.append((fpath, os.path.join('bin', fname)))

# ============================================================
# 二进制文件收集（NVIDIA CUDA DLL）
# ============================================================
# PyInstaller 自动收集 .pyd，但某些 NVIDIA CUDA DLL
# 可能通过 ctypes 动态加载，需要确保它们在 path 中
# CUDA DLL 通过 nvidia-* wheel packages 安装，PyInstaller 通常能自动发现
BINARIES = []

# 尝试收集 paddle 自带的 CUDA 库
try:
    import paddle
    paddle_dir = os.path.dirname(paddle.__file__)
    paddle_libs = os.path.join(paddle_dir, 'libs')
    if os.path.isdir(paddle_libs):
        for f in os.listdir(paddle_libs):
            if f.endswith('.dll') or f.endswith('.pyd'):
                fpath = os.path.join(paddle_libs, f)
                BINARIES.append((fpath, os.path.join('paddle', 'libs')))
except ImportError:
    pass

# ============================================================
# Analysis - PyInstaller 分析阶段
# ============================================================
a = Analysis(
    ['main.py'],
    pathex=[PROJECT_SRC],
    binaries=BINARIES,
    datas=DATAS,
    hiddenimports=HIDDEN_IMPORTS,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',           # 不打包 tkinter（使用 PyQt5）
        'pytest',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# ============================================================
# 数据文件由 post-COLLECT 代码统一复制，此处不再重复添加
# ============================================================

# ============================================================
# PYZ - Python 模块压缩包
# ============================================================
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# ============================================================
# EXE - 可执行文件
# ============================================================
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AVT_Subtitle_Processor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,     # Windows GUI 模式（不显示控制台）
    icon=None,
    target_arch=None,
    runtime_tmpdir=None,
)

# ============================================================
# EXE (Console) - 带控制台版本（调试用）
# ============================================================
exe_console = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AVT_Subtitle_Processor_Console',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,      # 显示控制台（调试用）
    icon=None,
    target_arch=None,
    runtime_tmpdir=None,
)

# ============================================================
# COLLECT - 收集所有文件到输出目录
# ============================================================
coll = COLLECT(
    exe,
    exe_console,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AVT_Subtitle_Processor',
)

# ============================================================
# 打包后复制缺失的模块数据文件到 dist（PyInstaller datas 参数不可靠，使用直接复制）
# 老版本已验证这些模块功能正常，只存在路径问题，不得删减
# ============================================================
import shutil

dist_dir = os.path.join(SPECPATH, 'dist', 'AVT_Subtitle_Processor', '_internal')

# venv site-packages（硬编码路径确保可靠性）
VENV_SITE = os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'Lib', 'site-packages')

def copy_dir_tree(src_dir, dst_dir, skip_pycache=True):
    """递归复制目录，保留老版本完整的模块组成"""
    if not os.path.isdir(src_dir):
        print(f"  [WARN] 源目录不存在: {src_dir}")
        return
    os.makedirs(dst_dir, exist_ok=True)
    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        d = os.path.join(dst_dir, item)
        if skip_pycache and item == '__pycache__':
            continue
        if os.path.isdir(s):
            copy_dir_tree(s, d, skip_pycache)
        elif os.path.isfile(s) and not os.path.exists(d):
            shutil.copy2(s, d)

print(f"[SPEC] VENV_SITE={VENV_SITE}")
print(f"[SPEC] dist_dir={dist_dir}")

# 1. 复制 bin 目录（FFmpeg）
bin_src = os.path.join(PROJECT_ROOT, 'bin')
if os.path.isdir(bin_src):
    bin_dst = os.path.join(dist_dir, 'bin')
    os.makedirs(bin_dst, exist_ok=True)
    for fn in os.listdir(bin_src):
        sfp = os.path.join(bin_src, fn)
        dfp = os.path.join(bin_dst, fn)
        if os.path.isfile(sfp) and not fn.endswith('.md'):
            # 如果目标路径被之前失败的 COLLECT 创建为目录，先删除
            if os.path.isdir(dfp):
                shutil.rmtree(dfp)
                print(f"[SPEC] 清理残留目录: bin/{fn}")
            if not os.path.exists(dfp):
                shutil.copy2(sfp, dfp)
                print(f"[SPEC] 已复制: bin/{fn}")

# 2. 复制 Cython/Utility（包含 CppSupport.cpp 等关键文件，缺失会导致 PaddleOCR 崩溃）
cython_utility_src = os.path.join(VENV_SITE, 'Cython', 'Utility')
if os.path.isdir(cython_utility_src):
    cython_utility_dst = os.path.join(dist_dir, 'Cython', 'Utility')
    print("[SPEC] 复制 Cython/Utility ...")
    copy_dir_tree(cython_utility_src, cython_utility_dst)
    print("[SPEC] Cython/Utility 完成")

# 3. 复制 NVIDIA CUDA 库（GPU 加速所需，老版本已验证）
nvidia_src = os.path.join(VENV_SITE, 'nvidia')
if os.path.isdir(nvidia_src):
    nvidia_dst = os.path.join(dist_dir, 'nvidia')
    print("[SPEC] 复制 nvidia/ CUDA 库...")
    copy_dir_tree(nvidia_src, nvidia_dst)
    print("[SPEC] nvidia/ 完成")

# 4. 复制 docx 模块
docx_src = os.path.join(VENV_SITE, 'docx')
if os.path.isdir(docx_src):
    docx_dst = os.path.join(dist_dir, 'docx')
    print("[SPEC] 复制 docx/ ...")
    copy_dir_tree(docx_src, docx_dst)
    print("[SPEC] docx/ 完成")

# 5. 复制 imageio 模块
imageio_src = os.path.join(VENV_SITE, 'imageio')
if os.path.isdir(imageio_src):
    imageio_dst = os.path.join(dist_dir, 'imageio')
    print("[SPEC] 复制 imageio/ ...")
    copy_dir_tree(imageio_src, imageio_dst)
    print("[SPEC] imageio/ 完成")

# 6. 复制完整 paddleocr 模块（老版本以独立目录存在，缺失会导致 ppocr 子模块加载失败）
paddleocr_src = os.path.join(VENV_SITE, 'paddleocr')
if os.path.isdir(paddleocr_src):
    paddleocr_dst = os.path.join(dist_dir, 'paddleocr')
    print("[SPEC] 复制 paddleocr/ ...")
    copy_dir_tree(paddleocr_src, paddleocr_dst)
    print("[SPEC] paddleocr/ 完成")

# 7. 复制完整 paddle 模块（老版本有 35+ 子目录，PyInstaller 只收集了 base+libs 到 PYZ）
paddle_src = os.path.join(VENV_SITE, 'paddle')
if os.path.isdir(paddle_src):
    paddle_dst = os.path.join(dist_dir, 'paddle')
    print("[SPEC] 复制 paddle/ 完整模块（跳过已存在的 base/libs）...")
    # 只补充缺失的子目录，避免覆盖已收集的文件
    for item in os.listdir(paddle_src):
        s = os.path.join(paddle_src, item)
        d = os.path.join(paddle_dst, item)
        if os.path.isdir(s):
            if not os.path.exists(d):
                copy_dir_tree(s, d)
        elif os.path.isfile(s) and not os.path.exists(d):
            shutil.copy2(s, d)
    print("[SPEC] paddle/ 完成")

# 7b. 复制 imgaug 模块（含 DejaVuSans.ttf 等数据文件，老版本以独立目录存在）
imgaug_src = os.path.join(VENV_SITE, 'imgaug')
if os.path.isdir(imgaug_src):
    imgaug_dst = os.path.join(dist_dir, 'imgaug')
    print("[SPEC] 复制 imgaug/ ...")
    copy_dir_tree(imgaug_src, imgaug_dst)
    print("[SPEC] imgaug/ 完成")

# 7c. 复制 unittest 模块（PyInstaller 硬编码排除，hidden imports 无效，Paddle cpp_extension 需要）
python_base = sys.base_prefix  # 基础 Python 安装目录（非 venv）
if not python_base:
    python_base = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
unittest_src = os.path.join(python_base, 'Lib', 'unittest')
if os.path.isdir(unittest_src):
    unittest_dst = os.path.join(dist_dir, 'unittest')
    print("[SPEC] 复制 unittest/ (PyInstaller 排除的标准库模块)...")
    copy_dir_tree(unittest_src, unittest_dst)
    # 清理 __pycache__
    pycache = os.path.join(unittest_dst, '__pycache__')
    if os.path.isdir(pycache):
        shutil.rmtree(pycache)
    print("[SPEC] unittest/ 完成")

# 8. 复制 nvidia .dist-info 元数据目录（保持与老版本一致）
for item in os.listdir(VENV_SITE):
    if item.startswith('nvidia_') and item.endswith('.dist-info'):
        src = os.path.join(VENV_SITE, item)
        dst = os.path.join(dist_dir, item)
        if os.path.isdir(src) and not os.path.exists(dst):
            copy_dir_tree(src, dst)
            print(f"[SPEC] 已复制: {item}")

# 9. 复制其他 .dist-info（保持与老版本一致）
for dist_prefix in ['paddleocr-', 'paddlepaddle_gpu-', 'cython-', 'imgaug-', 'lmdb-', 
                     'pyclipper-', 'scikit_image-', 'imageio-']:
    for item in os.listdir(VENV_SITE):
        if item.startswith(dist_prefix) and item.endswith('.dist-info'):
            src = os.path.join(VENV_SITE, item)
            dst = os.path.join(dist_dir, item)
            if os.path.isdir(src) and not os.path.exists(dst):
                copy_dir_tree(src, dst)
                print(f"[SPEC] 已复制: {item}")
                break

print("[SPEC] 缺失模块复制完成")

# 10. 清理所有 dist 中的 __pycache__、.egg-info、.pyc 等缓存（保持产物干净）
print("[SPEC] 清理 __pycache__ / .egg-info / .pyc 冗余缓存...")
for root, dirs, files in os.walk(dist_dir, topdown=False):
    for dname in list(dirs):
        if dname == '__pycache__' or dname.endswith('.egg-info'):
            p = os.path.join(root, dname)
            try:
                shutil.rmtree(p)
            except OSError:
                pass
    for fname in files:
        if fname.endswith('.pyc') or fname.endswith('.pyo'):
            p = os.path.join(root, fname)
            try:
                os.remove(p)
            except OSError:
                pass
print("[SPEC] 缓存清理完成")
# PaddleOCR GPU 详细使用教程

> **环境**：Windows 11 + RTX 4060 8GB + CUDA 12.x + PaddlePaddle-GPU 3.3.0 + PaddleOCR 2.8.1  
> **更新日期**：2026-05-22  
> **说明**：本文档为 PaddleOCR 独立使用教程，与 AVT 字幕处理器主程序中的 OCR 集成方式不同。AVT 应用通过 [subtitle_engine.py](../modules/subtitle_engine.py) 的 `_get_ocr_engine()` 方法调用 PaddleOCR。

---

## 目录

1. [环境信息](#环境信息)
2. [快速开始](#快速开始)
3. [命令行使用](#命令行使用)
4. [Python API 使用](#python-api-使用)
5. [日文 OCR 专项](#日文-ocr-专项)
6. [常用参数详解](#常用参数详解)
7. [输出结果解析](#输出结果解析)
8. [图像预处理优化](#图像预处理优化)
9. [批量处理](#批量处理)
10. [故障排除](#故障排除)

---

## 环境信息

### 关键路径

| 组件 | 路径 |
|------|------|
| **虚拟环境** | `D:\Software\PaddleOCR_gpu\venv\` |
| **Python 可执行文件** | `D:\Software\PaddleOCR_gpu\venv\Scripts\python.exe` |
| **pip 可执行文件** | `D:\Software\PaddleOCR_gpu\venv\Scripts\pip3.exe` |
| **PaddleOCR 包路径** | `D:\Software\PaddleOCR_gpu\venv\Lib\site-packages\paddleocr\` |
| **paddleocr.py 主文件** | `D:\Software\PaddleOCR_gpu\venv\Lib\site-packages\paddleocr\paddleocr.py` |
| **优化脚本** | `D:\Software\PaddleOCR_gpu\test_optimize.py` |
| **识别结果输出** | `D:\Software\PaddleOCR_gpu\ocr_result.txt` |

### 版本信息

```powershell
# 激活虚拟环境
& "D:\Software\PaddleOCR_gpu\venv\Scripts\Activate.ps1"

# 查看版本
python -c "import paddle; print('PaddlePaddle:', paddle.__version__)"
python -c "import paddleocr; print('PaddleOCR:', paddleocr.__version__)"
```

当前版本：
- PaddlePaddle-GPU: **3.3.0**
- PaddleOCR: **2.8.1**
- CuDNN: **9.9.0.52**

### GPU 验证

```powershell
& "D:\Software\PaddleOCR_gpu\venv\Scripts\python.exe" -c "import paddle; print('GPU可用:', paddle.base.is_compiled_with_cuda())"
```

---

## 快速开始

### 方式一：命令行（推荐）

```powershell
# 进入工作目录
cd D:\Software\PaddleOCR_gpu

# 激活虚拟环境
& .\venv\Scripts\Activate.ps1

# 单行文本识别（日文）
paddleocr --image_dir "D:\path\to\image.png" --lang japan --use_gpu true

# 保存到文件
paddleocr --image_dir "D:\path\to\image.png" --lang japan --use_gpu true > result.txt
```

### 方式二：Python 脚本

```python
from paddleocr import PaddleOCR

# 初始化（只需执行一次）
ocr = PaddleOCR(
    lang='japan',        # 日文识别
    use_gpu=True,        # 使用 GPU
    gpu_mem=500,         # GPU 显存限制（MB），RTX 4060 8GB 可设 4000-6000
    det_db_thresh=0.3,  # 检测阈值（可调）
    det_db_box_thresh=0.5,
    show_log=True        # 显示详细日志
)

# 识别单张图片
result = ocr.ocr("D:\path\to\image.png")

# 打印结果
for line in result[0]:
    print(f"文本: {line[1][0]}")
    print(f"置信度: {line[1][1]:.4f}")
    print(f"边界框: {line[0]}")
    print("-" * 50)
```

---

## 命令行使用

### 基础命令格式

```powershell
paddleocr [选项]
```

### 常用命令行参数

#### 输入参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--image_dir` | 输入图片路径（单张或目录） | `--image_dir "D:\images\test.png"` |
| `--image_dir` | 批量识别整个目录 | `--image_dir "D:\images\"` |
| `--type` | 识别类型：`ocr`（默认）或 `structure`（文档结构） | `--type structure` |

#### 语言参数

| 参数 | 说明 | 支持语言 |
|------|------|----------|
| `--lang ch` | 简体中文 | ✅ |
| `--lang en` | 英文 | ✅ |
| `--lang japan` | 日文 | ✅ **（当前默认）** |
| `--lang korean` | 韩文 | ✅ |
| `--lang ch_tra` | 繁体中文 | ✅ |
| `--lang german` | 德语 | ✅ |
| `--lang french` | 法语 | ✅ |

> **注意**：`paddleocr.py` 中 `--lang` 默认值已改为 `japan`（原默认 `ch`）

#### GPU 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--use_gpu` | 是否使用 GPU | `true` |
| `--gpu_mem` | GPU 显存限制（MB） | `500` |
| `--use_tensorrt` | 使用 TensorRT 加速 | `false` |

#### 检测参数（文字检测）

| 参数 | 说明 | 默认值 | 建议值 |
|------|------|--------|--------|
| `--det_db_thresh` | 检测阈值 | `0.3` | `0.2-0.4` |
| `--det_db_box_thresh` | 边框阈值 | `0.5` | `0.4-0.6` |
| `--det_db_unclip_ratio` | 边框膨胀率 | `1.5` | `1.5-2.5` |
| `--det_limit_side_len` | 限制图像长边 | `960` | `960-1920` |

#### 识别参数（文字识别）

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--rec_batch_num` | 识别批大小 | `6` |
| `--rec_img_h` | 识别图像高度 | `48` |
| `--rec_img_w` | 识别图像宽度 | `320` |

#### 方向分类参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--use_angle_cls` | 使用方向分类 | `false` |
| `--cls_thresh` | 方向分类阈值 | `0.9` |

#### 输出参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--draw_img_save_dir` | 绘制结果保存目录 | `--draw_img_save_dir ./output` |
| `--save_crop_res` | 保存裁剪结果 | `--save_crop_res true` |
| `--crop_res_save_dir` | 裁剪结果保存目录 | `--crop_res_save_dir ./crops` |

### 完整命令行示例

```powershell
# 示例 1：日文图片识别（详细输出）
paddleocr `
    --image_dir "D:\test\japanese_text.png" `
    --lang japan `
    --use_gpu true `
    --gpu_mem 4000 `
    --det_db_thresh 0.3 `
    --det_db_box_thresh 0.5 `
    --rec_batch_num 6 `
    --draw_img_save_dir "D:\test\output" `
    --show_log true

# 示例 2：批量识别整个目录
paddleocr `
    --image_dir "D:\test\images\" `
    --lang japan `
    --use_gpu true `
    --draw_img_save_dir "D:\test\output"

# 示例 3：中文识别（方向分类）
paddleocr `
    --image_dir "D:\test\chinese.png" `
    --lang ch `
    --use_gpu true `
    --use_angle_cls true `
    --cls_thresh 0.9
```

---

## Python API 使用

### 基础使用

```python
from paddleocr import PaddleOCR

# 初始化 OCR 引擎
ocr = PaddleOCR(
    lang='japan',       # 语言
    use_gpu=True,       # 使用 GPU
    gpu_mem=4000,       # GPU 显存限制（MB）
    show_log=False      # 不显示日志
)

# 识别图片
result = ocr.ocr("D:\test\image.png")

# result 结构：
# [
#   [                      # 第一页（单张图片只有一页）
#     [
#       [[x1,y1], [x2,y2], [x3,y3], [x4,y4]],  # 文本框坐标
#       ('识别文本', 0.9876)                      # 文本 + 置信度
#     ],
#     ...
#   ]
# ]

# 遍历结果
for line in result[0]:
    box = line[0]          # 边界框坐标
    text = line[1][0]     # 识别文本
    conf = line[1][1]     # 置信度
    print(f"[{conf:.4f}] {text}")
```

### 批量识别

```python
import os
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang='japan', use_gpu=True, show_log=False)

image_dir = r"D:\test\images"
output_file = r"D:\test\results.txt"

with open(output_file, 'w', encoding='utf-8') as f:
    for filename in os.listdir(image_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(image_dir, filename)
            print(f"正在识别: {filename}")
            
            result = ocr.ocr(filepath)
            
            f.write(f"=== {filename} ===\n")
            if result and result[0]:
                for line in result[0]:
                    text = line[1][0]
                    conf = line[1][1]
                    f.write(f"[{conf:.4f}] {text}\n")
            else:
                f.write("（未识别到文本）\n")
            f.write("\n")

print("批量识别完成！")
```

### 保存可视化结果

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang='japan', use_gpu=True)

# 识别并保存可视化结果
result = ocr.ocr(
    "D:\test\image.png",
    det=True,          # 检测
    rec=True,          # 识别
    cls=False,         # 方向分类（可选）
    save_crop_res=True,# 保存裁剪区域
)

# 可视化结果会保存在 ./inference_results/ 目录
# 包含：检测框绘制后的图片
```

---

## 日文 OCR 专项

### 日文识别特点

1. **假名识别**：平假名（ひらがな）和片假名（カタカナ）均支持
2. **汉字识别**：中日汉字（Kanji）识别效果较好
3. **常见错误**：
   - 假名 せぇ/せえ 混淆
   - 省略号（…）丢失
   - 长音 ー 误识为一

### 优化日文识别的预处理脚本

已创建优化脚本：`D:\Software\PaddleOCR_gpu\test_optimize.py`

```python
# test_optimize.py 的核心逻辑

import cv2
import numpy as np
from paddleocr import PaddleOCR

def preprocess_image(image_path):
    """图像预处理"""
    img = cv2.imread(image_path)
    
    # 1. 放大图像（提高小字识别率）
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # 2. 降噪（可选）
    img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    
    # 3. 二值化（可选，适用于清晰文档）
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    
    return img

def postprocess_text(text):
    """后处理：修正常见错误"""
    # 修正假名混淆
    corrections = {
        'せぇ': 'せえ',
        'てぇ': 'てえ',
        # 添加更多规则...
    }
    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)
    return text

# 使用
ocr = PaddleOCR(lang='japan', use_gpu=True)
img = preprocess_image("D:\test\japanese.png")
result = ocr.ocr(img)

for line in result[0]:
    raw_text = line[1][0]
    corrected_text = postprocess_text(raw_text)
    print(f"原始: {raw_text}")
    print(f"修正: {corrected_text}")
```

### 运行优化脚本

```powershell
cd D:\Software\PaddleOCR_gpu
& ".\venv\Scripts\python.exe" "test_optimize.py"
```

---

## 常用参数详解

### 检测参数（Det - 文字检测）

文字检测用于在图像中定位文字区域。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--det` | bool | `true` | 是否执行检测 |
| `--det_db_thresh` | float | `0.3` | DB 算法二值化阈值，**值越低越敏感** |
| `--det_db_box_thresh` | float | `0.5` | 检测框置信度阈值，**值越低框越多** |
| `--det_db_unclip_ratio` | float | `1.5` | 检测框膨胀率，**值越大框越大** |
| `--det_db_score_mode` | str | `fast` | 评分模式：`fast` 或 `slow` |
| `--det_limit_side_len` | int | `960` | 图像长边限制，**增大可提高小字识别** |
| `--det_limit_type` | str | `max` | 限制类型：`max`（长边）或 `min`（短边） |

#### 调参建议

**场景 1：清晰文档（扫描件、白底黑字）**
```powershell
paddleocr --image_dir doc.png --lang japan `
    --det_db_thresh 0.3 `
    --det_db_box_thresh 0.5 `
    --det_limit_side_len 960
```

**场景 2：复杂背景（漫画、自然场景）**
```powershell
paddleocr --image_dir comic.png --lang japan `
    --det_db_thresh 0.2 `       # 降低阈值，更敏感
    --det_db_box_thresh 0.4 `   # 降低框阈值
    --det_db_unclip_ratio 2.0 ` # 增大膨胀率
    --det_limit_side_len 1920    # 增大图像尺寸
```

### 识别参数（Rec - 文字识别）

文字识别用于将检测到的文字区域转换为文本。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--rec` | bool | `true` | 是否执行识别 |
| `--rec_img_h` | int | `48` | 识别图像高度 |
| `--rec_img_w` | int | `320` | 识别图像宽度（日文可适当增大） |
| `--rec_batch_num` | int | `6` | 批处理大小（GPU 可增大） |

### 方向分类参数（Cls - 方向分类）

用于检测文字方向（0°、90°、180°、270°）。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--use_angle_cls` | bool | `false` | 是否使用方向分类 |
| `--cls_thresh` | float | `0.9` | 方向分类置信度阈值 |
| `--cls_batch_num` | int | `6` | 批处理大小 |

> **建议**：仅当图片可能旋转时才启用（会增加耗时）

---

## 输出结果解析

### 命令行输出格式

```
[2026/05/20 16:08:00] ppocr DEBUG: dt_boxes num : 5, elapsed : 0.677s
[2026/05/20 16:08:00] ppocr DEBUG: cls num  : 5, elapsed : 0.145s
[2026/05/20 16:08:00] ppocr DEBUG: rec_res num  : 5, elapsed : 0.160s

テストtext1  0.9987
テストtext2  0.9876
テストtext3  0.5432
...
```

- `dt_boxes num`: 检测到的文字区域数量
- `elapsed`: 各阶段耗时（秒）
- `文本  置信度`: 识别结果

### Python API 返回结构

```python
result = ocr.ocr("image.png")

# result 是一个嵌套列表：
[
  [                      # 页面（第 1 页）
    [                    # 第 1 个检测框
      [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],  # 边界框（4 个角点）
      ('识别文本', 0.9876)                           # (文本, 置信度)
    ],
    [                    # 第 2 个检测框
      [[...], [...], [...], [...]],
      ('文本2', 0.5432)
    ],
    ...
  ]
]
```

### 边界框坐标说明

```
(x1,y1) -------- (x2,y2)
   |                  |
   |     文字区域      |
   |                  |
(x4,y4) -------- (x3,y3)
```

- 左上角: (x1, y1)
- 右上角: (x2, y2)
- 右下角: (x3, y3)
- 左下角: (x4, y4)

### 保存到文件

```python
import json

result = ocr.ocr("image.png")

# 保存为 JSON
with open('result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# 保存为 TXT（纯文本）
with open('result.txt', 'w', encoding='utf-8') as f:
    for line in result[0]:
        text = line[1][0]
        conf = line[1][1]
        f.write(f"[{conf:.4f}] {text}\n")
```

---

## 图像预处理优化

### 为什么需要预处理？

PaddleOCR 对以下情况效果可能不佳：
1. 图像模糊
2. 文字过小
3. 光照不均
4. 背景复杂（如漫画网点）

### 预处理脚本模板

```python
import cv2
import numpy as np

def preprocess_for_ocr(image_path, output_path=None):
    """
    为 OCR 优化图像预处理
    """
    img = cv2.imread(image_path)
    
    # 步骤 1：放大（提高小字识别率）
    scale = 2.0
    img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    # 步骤 2：转灰度
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 步骤 3：降噪（可选）
    # 方法 A：高斯模糊
    denoised = cv2.GaussianBlur(gray, (3, 3), 0)
    # 方法 B：非局部均值去噪（效果更好但更慢）
    # denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # 步骤 4：二值化（适用于文档）
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 步骤 5：形态学操作（去除噪点）
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
    # 转回 BGR（PaddleOCR 需要 3 通道）
    result = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)
    
    if output_path:
        cv2.imwrite(output_path, result)
        print(f"预处理完成，保存至: {output_path}")
    
    return result

# 使用
preprocessed = preprocess_for_ocr(
    "D:\test\japanese_comic.png",
    "D:\test\japanese_comic_preprocessed.png"
)

# 用预处理后的图像进行 OCR
result = ocr.ocr(preprocessed)
```

### 针对不同场景的预处理策略

**场景 1：清晰文档（扫描件）**
```python
# 只需简单二值化
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
```

**场景 2：漫画/复杂背景**
```python
# 需要更多步骤
# 1. 放大
# 2. 颜色空间转换（转 HSV 提取文字）
# 3. 自适应二值化
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# ... 根据具体情况调整
```

**场景 3：模糊图像**
```python
# 锐化
kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
sharpened = cv2.filter2D(img, -1, kernel)
```

---

## 批量处理

### 批量识别整个目录

```powershell
# 命令行方式
cd D:\Software\PaddleOCR_gpu
& .\venv\Scripts\Activate.ps1
paddleocr --image_dir "D:\test\images\" --lang japan --use_gpu true --draw_img_save_dir "D:\test\output"
```

### Python 批量处理脚本

```python
import os
import cv2
from paddleocr import PaddleOCR

class BatchOCR:
    def __init__(self, lang='japan', use_gpu=True):
        self.ocr = PaddleOCR(lang=lang, use_gpu=use_gpu, show_log=False)
        self.results = {}
    
    def process_directory(self, input_dir, output_dir):
        """批量处理目录"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取所有图片文件
        image_files = [
            f for f in os.listdir(input_dir)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))
        ]
        
        print(f"找到 {len(image_files)} 个图片文件")
        
        for i, filename in enumerate(image_files, 1):
            print(f"[{i}/{len(image_files)}] 处理: {filename}")
            filepath = os.path.join(input_dir, filename)
            
            try:
                # 识别
                result = self.ocr.ocr(filepath)
                
                # 保存文本结果
                base_name = os.path.splitext(filename)[0]
                output_file = os.path.join(output_dir, f"{base_name}.txt")
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"源文件: {filename}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    if result and result[0]:
                        for j, line in enumerate(result[0], 1):
                            text = line[1][0]
                            conf = line[1][1]
                            f.write(f"{j}. [{conf:.4f}] {text}\n")
                    else:
                        f.write("（未识别到文本）\n")
                
                print(f"  → 结果已保存: {output_file}")
                
            except Exception as e:
                print(f"  ✗ 错误: {e}")
        
        print("\n批量处理完成！")

# 使用
batch_ocr = BatchOCR(lang='japan', use_gpu=True)
batch_ocr.process_directory(
    input_dir=r"D:\test\images",
    output_dir=r"D:\test\results"
)
```

---

## 故障排除

### 问题 1：GPU 不可用

**症状**：
```
GPU available: False
```

**解决方案**：
1. 检查 PaddlePaddle 是否 GPU 版本：
   ```powershell
   pip list | findstr paddlepaddle
   ```
   - 如果是 `paddlepaddle`（CPU 版），卸载并安装 `paddlepaddle-gpu`
   
2. 检查 CUDA 和 cuDNN 版本兼容性
   - PaddlePaddle 3.3.0 需要 CUDA 12.6 + cuDNN 9.9+

### 问题 2：识别准确率低

**解决方案**：
1. **图像预处理**：放大、去噪、二值化
2. **调整检测参数**：
   ```powershell
   paddleocr --image_dir test.png --lang japan `
       --det_db_thresh 0.2 `
       --det_db_box_thresh 0.4 `
       --det_limit_side_len 1920
   ```
3. **后处理**：添加常见错误修正规则

### 问题 3：显存不足（Out of Memory）

**症状**：
```
CUDA out of memory
```

**解决方案**：
1. 降低 `gpu_mem` 参数：
   ```powershell
   paddleocr --image_dir test.png --use_gpu true --gpu_mem 2000
   ```
   
2. 减小 `det_limit_side_len`：
   ```powershell
   paddleocr --image_dir test.png --det_limit_side_len 960
   ```

### 问题 4：命令行 `paddleocr` 不可用

**解决方案**：
1. 确保已激活虚拟环境：
   ```powershell
   & "D:\Software\PaddleOCR_gpu\venv\Scripts\Activate.ps1"
   ```
   
2. 或使用完整 Python 路径：
   ```powershell
   & "D:\Software\PaddleOCR_gpu\venv\Scripts\python.exe" -m paddleocr.paddleocr --image_dir test.png
   ```

### 问题 5：cuDNN 版本警告

**症状**：
```
W0508 XX:XX:XX.XXXXXX XX gpu_resources.cc:116] cuDNN version XX is not suited for paddle compiled with cuDNN version YY
```

**解决方案**：
1. 升级 cuDNN 至 Paddle 编译版本：
   ```powershell
   & "D:\Software\PaddleOCR_gpu\venv\Scripts\pip3.exe" install nvidia-cudnn-cu12==YY.Y.YY.YY
   ```
   
2. 或忽略警告（非致命错误）

---

## 附录：完整路径速查表

### 执行命令

| 操作 | 命令 |
|------|------|
| **激活虚拟环境** | `& "D:\Software\PaddleOCR_gpu\venv\Scripts\Activate.ps1"` |
| **运行 PaddleOCR CLI** | `paddleocr --image_dir "路径" --lang japan` |
| **运行优化脚本** | `& "D:\Software\PaddleOCR_gpu\venv\Scripts\python.exe" "D:\Software\PaddleOCR_gpu\test_optimize.py"` |
| **Python 交互模式** | `& "D:\Software\PaddleOCR_gpu\venv\Scripts\python.exe"` |

### 配置文件

| 文件 | 路径 | 用途 |
|------|------|------|
| **paddleocr.py** | `D:\Software\PaddleOCR_gpu\venv\Lib\site-packages\paddleocr\paddleocr.py` | 主程序，可修改默认参数 |
| **优化脚本** | `D:\Software\PaddleOCR_gpu\test_optimize.py` | 预处理+后处理示例 |
| **识别结果** | `D:\Software\PaddleOCR_gpu\ocr_result.txt` | 默认输出文件 |

### 模型文件

PaddleOCR 会自动下载模型至：
- **检测模型**：`C:\Users\liket\.paddleocr\whl\det\`
- **识别模型**：`C:\Users\liket\.paddleocr\whl\rec\`
- **方向分类模型**：`C:\Users\liket\.paddleocr\whl\cls\`

---

## 总结

本教程涵盖了 PaddleOCR GPU 版本的：
- ✅ 环境配置与验证
- ✅ 命令行与 Python API 使用
- ✅ 日文 OCR 专项优化
- ✅ 参数详解与调优建议
- ✅ 批量处理脚本
- ✅ 常见问题排查

如有更多问题，参考官方文档：https://paddlepaddle.github.io/PaddleOCR/

---
*最后更新：2026-05-22*
*环境：Windows 11 + RTX 4060 + PaddlePaddle-GPU 3.3.0 + PaddleOCR 2.8.1*

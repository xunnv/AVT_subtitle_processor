"""
字幕处理引擎模块
整合字幕提取、翻译、烧录的完整流程
"""

import os
import sys
import re
import json
import time
import subprocess
import shutil
import hashlib
import requests
import glob
import ctypes
from pathlib import Path
from datetime import timedelta
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from .logger import logger
from .security import PathSecurity

# 隐藏控制台窗口的配置
def _get_subprocess_startupinfo():
    """获取隐藏控制台窗口的 startupinfo（仅 Windows）"""
    startupinfo = None
    if sys.platform == 'win32':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
    return startupinfo

_SUBPROCESS_STARTUPINFO = _get_subprocess_startupinfo()

from .translator import TranslatorFactory


@dataclass
class SubtitleItem:
    """字幕条目"""
    start: float
    end: float
    text: str
    translation: str = ""

    def to_dict(self) -> Dict:
        return {
            'start': self.start,
            'end': self.end,
            'text': self.text,
            'translation': self.translation
        }


@dataclass
class ProcessResult:
    """处理结果"""
    success: bool
    message: str
    output_video: str = ""
    subtitle_srt: str = ""
    subtitle_ass: str = ""
    statistics: Dict = None

    def __post_init__(self):
        if self.statistics is None:
            self.statistics = {}


class SubtitleEngine:
    """字幕处理引擎"""

    def __init__(self, config_manager):
        self.config = config_manager
        self._setup_cuda_dll()
        self.progress_callback: Optional[Callable] = None
        self.cancel_requested = False
        self.translator = None
        self._init_translator()
        self._ocr_engine = None

    def _setup_cuda_dll(self):
        """配置CUDA DLL路径"""
        paddleocr_paths = [
            os.environ.get("PADDLEOCR_VENV", ""),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "paddleocr_env"),
        ]
        
        venv_site = None
        for path in paddleocr_paths:
            if path:
                site_path = os.path.join(path, "Lib", "site-packages")
                if os.path.isdir(site_path):
                    venv_site = site_path
                    break
        
        if not venv_site:
            return
        
        cuda_dirs = [
            os.path.join(venv_site, "nvidia", "cudnn", "bin"),
            os.path.join(venv_site, "nvidia", "cublas", "bin"),
            os.path.join(venv_site, "nvidia", "cufft", "bin"),
            os.path.join(venv_site, "nvidia", "curand", "bin"),
            os.path.join(venv_site, "nvidia", "cusolver", "bin"),
            os.path.join(venv_site, "nvidia", "cusparse", "bin"),
            os.path.join(venv_site, "nvidia", "cudart", "bin"),
        ]

        for dll_dir in cuda_dirs:
            if os.path.isdir(dll_dir) and dll_dir not in os.environ["PATH"]:
                os.environ["PATH"] = dll_dir + ";" + os.environ["PATH"]

        try:
            cudnn_dll = os.path.join(venv_site, "nvidia", "cudnn", "bin", "cudnn64_8.dll")
            if os.path.exists(cudnn_dll):
                ctypes.CDLL(cudnn_dll)
        except Exception:
            pass

    def _init_translator(self):
        """初始化翻译器"""
        trans_config = self.config.get_translation_config()
        framework = trans_config.get('framework', 'ollama')
        try:
            self.translator = TranslatorFactory.create(framework, trans_config)
            logger.info(f"翻译器初始化成功: {framework}")
        except Exception as e:
            logger.error(f"翻译器初始化失败: {e}")
            self.translator = None

    def reload_translator(self):
        """重新加载翻译器"""
        self._init_translator()

    def _get_ocr_engine(self):
        """获取 OCR 引擎实例（单例模式，延迟初始化）"""
        if self._ocr_engine is None:
            from paddleocr import PaddleOCR
            
            ocr_config = self.config.get_ocr_config()
            self._ocr_engine = PaddleOCR(
                use_angle_cls=False,
                lang=ocr_config.get('lang', 'japan'),
                use_gpu=ocr_config.get('use_gpu', True),
                enable_mkldnn=ocr_config.get('enable_mkldnn', False),
                det_db_thresh=ocr_config.get('det_db_thresh', 0.3),
                det_db_box_thresh=ocr_config.get('det_db_box_thresh', 0.5),
                rec_score_thresh=ocr_config.get('rec_score_thresh', 0.5),
                show_log=False
            )
        return self._ocr_engine

    def reset_ocr_engine(self):
        """重置 OCR 引擎（配置变更时调用）"""
        if self._ocr_engine is not None:
            del self._ocr_engine
            self._ocr_engine = None

    def set_progress_callback(self, callback: Callable):
        """设置进度回调函数"""
        self.progress_callback = callback

    def request_cancel(self):
        """请求取消处理"""
        self.cancel_requested = True

    def _report_progress(self, step: int, total_steps: int,
                        progress: float, message: str, eta: str = ""):
        """报告进度"""
        if self.progress_callback:
            self.progress_callback(step, total_steps, progress, message, eta)

    def process_video(self, video_path: str) -> ProcessResult:
        """处理单个视频（支持断点续传）"""
        self.cancel_requested = False
        start_time = time.time()
        video_name = Path(video_path).stem
        
        logger.info(f"开始处理视频: {video_path}")

        ffmpeg_ok, ffmpeg_msg = self._check_ffmpeg()
        if not ffmpeg_ok:
            logger.error(f"FFmpeg 检查失败: {ffmpeg_msg}")
            return ProcessResult(False, f"FFmpeg 检查失败: {ffmpeg_msg}")

        if not self.translator:
            self.reload_translator()
            if not self.translator:
                logger.error("翻译器未初始化")
                return ProcessResult(False, "翻译器未初始化，请检查配置")

        try:
            valid, msg = PathSecurity.validate_video_file(video_path)
            if not valid:
                logger.error(f"视频文件验证失败: {msg}")
                return ProcessResult(False, msg)
            
            output_dir = self.config.get('paths.output_dir', '')
            valid, msg = PathSecurity.validate_output_path(output_dir)
            if not valid:
                logger.error(f"输出目录验证失败: {msg}")
                return ProcessResult(False, msg)

            video_hash = hashlib.md5(video_path.encode()).hexdigest()[:8]
            work_dir = os.path.join(output_dir, f"work_{video_hash}")
            frames_dir = os.path.join(work_dir, "frames")
            os.makedirs(frames_dir, exist_ok=True)

            video_info = self._get_video_info(video_path)

            subtitles_dir = os.path.join(output_dir, "subtitles")
            videos_dir = os.path.join(output_dir, "videos")
            os.makedirs(subtitles_dir, exist_ok=True)
            os.makedirs(videos_dir, exist_ok=True)

            srt_path = os.path.join(subtitles_dir, f"{video_name}.srt")
            ass_path = os.path.join(subtitles_dir, f"{video_name}.ass")
            output_video = os.path.join(videos_dir, f"{video_name}_subtitled.mp4")

            if os.path.exists(output_video):
                logger.info(f"检测到已完成的输出视频，跳过处理: {output_video}")
                self._report_progress(6, 6, 100, f"检测到已完成的输出视频，跳过处理")
                elapsed = time.time() - start_time
                return ProcessResult(
                    True,
                    f"检测到已完成的输出视频，跳过处理",
                    output_video=output_video,
                    subtitle_srt=srt_path if os.path.exists(srt_path) else "",
                    subtitle_ass=ass_path if os.path.exists(ass_path) else "",
                    statistics={'elapsed_time': elapsed}
                )

            self._report_progress(1, 6, 0, "正在提取视频帧...")
            frames = sorted(glob.glob(os.path.join(frames_dir, "*.jpg")))
            if frames:
                logger.info(f"检测到已提取的帧({len(frames)}帧)，跳过帧提取")
                self._report_progress(1, 6, 100, "检测到已提取的帧，跳过帧提取")
            else:
                try:
                    frames = self._extract_frames(video_path, frames_dir)
                    logger.info(f"帧提取完成，共提取 {len(frames)} 帧")
                except RuntimeError as e:
                    logger.error(f"帧提取失败: {e}")
                    return ProcessResult(False, str(e))
                if not frames:
                    logger.error("帧提取失败：未提取到任何帧")
                    return ProcessResult(False, "帧提取失败")

            self._report_progress(2, 6, 0, "正在进行OCR识别...")
            raw_subtitles = []
            if os.path.exists(srt_path):
                logger.info(f"检测到已生成的SRT文件，跳过OCR和翻译")
                self._report_progress(2, 6, 100, "检测到已生成的SRT文件，跳过OCR和翻译")
                self._report_progress(3, 6, 100, "跳过字幕整理")
                self._report_progress(4, 6, 100, "跳过翻译")
                subtitles = self._load_subtitles_from_srt(srt_path)
            else:
                raw_subtitles = self._ocr_recognize(frames)
                logger.info(f"OCR识别完成，识别到 {len(raw_subtitles)} 条字幕")
                if self.cancel_requested:
                    logger.info("用户取消处理")
                    return ProcessResult(False, "用户取消")
                if not raw_subtitles:
                    logger.warning("未识别到字幕")
                    return ProcessResult(False, "未识别到字幕")

                self._report_progress(3, 6, 50, "正在整理字幕...")
                subtitles = self._organize_subtitles(raw_subtitles)
                logger.info(f"字幕整理完成，共整理 {len(subtitles)} 条")

                self._report_progress(4, 6, 0, "正在进行翻译...")
                subtitles = self._translate_subtitles(subtitles)
                logger.info(f"翻译完成，共翻译 {len(subtitles)} 条")
                if self.cancel_requested:
                    logger.info("用户取消处理")
                    return ProcessResult(False, "用户取消")

                self._save_srt(subtitles, srt_path)
                logger.info(f"SRT字幕已保存: {srt_path}")

            self._report_progress(5, 6, 0, "正在生成ASS字幕...")
            if os.path.exists(ass_path):
                logger.info(f"检测到已生成的ASS文件，跳过ASS生成")
                self._report_progress(5, 6, 100, "检测到已生成的ASS文件，跳过ASS生成")
            else:
                self._generate_ass(subtitles, ass_path, video_info)
                logger.info(f"ASS字幕已生成: {ass_path}")

            self._report_progress(6, 6, 0, "正在烧录字幕...")
            success, error_detail = self._burn_subtitles(video_path, ass_path, output_video)

            if not success:
                logger.error(f"字幕烧录失败: {error_detail}")
                return ProcessResult(False, f"字幕烧录失败: {error_detail}")
            
            logger.info(f"字幕烧录完成: {output_video}")

            if self.config.get('processing.cleanup_temp', True):
                shutil.rmtree(work_dir)
                logger.debug(f"临时目录已清理: {work_dir}")

            elapsed = time.time() - start_time
            logger.info(f"视频处理完成: {video_name}，耗时 {elapsed:.2f} 秒")
            
            return ProcessResult(
                True,
                f"处理完成，耗时 {elapsed:.0f} 秒",
                output_video=output_video,
                subtitle_srt=srt_path,
                subtitle_ass=ass_path,
                statistics={
                    'total_frames': len(frames),
                    'subtitle_count': len(subtitles),
                    'elapsed_time': elapsed
                }
            )

        except Exception as e:
            logger.exception(f"视频处理异常: {video_path}")
            return ProcessResult(False, f"处理异常: {str(e)}")

    def _load_subtitles_from_srt(self, srt_path: str) -> List[SubtitleItem]:
        """从SRT文件加载字幕"""
        subtitles = []
        try:
            with open(srt_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            blocks = re.split(r'\n\n+', content.strip())
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    try:
                        idx = int(lines[0])
                        time_line = lines[1]
                        text_lines = lines[2:]
                        
                        match = re.match(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)', time_line)
                        if match:
                            start = int(match.group(1)) * 3600 + int(match.group(2)) * 60 + int(match.group(3)) + int(match.group(4)) / 1000
                            end = int(match.group(5)) * 3600 + int(match.group(6)) * 60 + int(match.group(7)) + int(match.group(8)) / 1000
                            
                            text = ""
                            translation = ""
                            if len(text_lines) >= 2:
                                text = text_lines[0]
                                translation = text_lines[1]
                            else:
                                text = "\n".join(text_lines)
                            
                            subtitles.append(SubtitleItem(start=start, end=end, text=text, translation=translation))
                    except Exception:
                        continue
        except Exception:
            pass
        
        return subtitles

    def _get_video_info(self, video_path: str) -> Dict[str, Any]:
        """获取视频信息"""
        ffprobe = self.config.get('paths.ffprobe_path', 'ffprobe')
        cmd = [ffprobe, "-v", "quiet", "-print_format", "json",
               "-show_format", "-show_streams", video_path]

        result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore', timeout=30, startupinfo=_SUBPROCESS_STARTUPINFO)
        if result.returncode != 0 or not result.stdout:
            return {"duration": 0, "width": 1920, "height": 1080, "fps": 30.0, "fps_str": "30000/1001"}

        info = json.loads(result.stdout)
        duration = float(info["format"]["duration"])
        video_stream = next((s for s in info["streams"] if s["codec_type"] == "video"), None)

        if not video_stream:
            return {"duration": duration, "width": 1920, "height": 1080, "fps": 30.0, "fps_str": "30000/1001"}

        width = int(video_stream["width"])
        height = int(video_stream["height"])
        fps_str = video_stream["r_frame_rate"]

        fps = self._parse_fps(fps_str)

        return {
            "duration": duration,
            "width": width,
            "height": height,
            "fps": fps,
            "fps_str": fps_str
        }

    def _parse_fps(self, fps_str: str) -> float:
        """安全解析帧率字符串"""
        try:
            if '/' in fps_str:
                parts = fps_str.split('/')
                return float(parts[0]) / float(parts[1])
            return float(fps_str)
        except (ValueError, ZeroDivisionError):
            return 30.0

    def _check_ffmpeg(self) -> tuple[bool, str]:
        """检查 FFmpeg 是否可用"""
        ffmpeg = self.config.get('paths.ffmpeg_path', 'ffmpeg')
        try:
            result = subprocess.run([ffmpeg, "-version"], capture_output=True, text=True, timeout=10, startupinfo=_SUBPROCESS_STARTUPINFO)
            if result.returncode == 0:
                return True, "FFmpeg 可用"
            return False, f"FFmpeg 运行失败"
        except FileNotFoundError:
            return False, f"FFmpeg 未找到: {ffmpeg}"
        except Exception as e:
            return False, f"FFmpeg 检查失败: {str(e)}"

    def _extract_frames(self, video_path: str, frames_dir: str) -> List[str]:
        """提取视频帧"""
        ffmpeg = self.config.get('paths.ffmpeg_path', 'ffmpeg')
        interval = self.config.get('ocr.frame_interval', 1)
        quality = self.config.get('ocr.frame_quality', 2)

        cmd = [ffmpeg, "-y", "-i", video_path,
               "-vf", f"fps=1/{interval}",
               "-q:v", str(quality),
               os.path.join(frames_dir, "frame_%06d.jpg")]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600, startupinfo=_SUBPROCESS_STARTUPINFO)
        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else "帧提取失败"
            raise RuntimeError(f"FFmpeg 错误: {error_msg}")

        return sorted(glob.glob(os.path.join(frames_dir, "*.jpg")))

    def _ocr_recognize(self, frames: List[str]) -> List[Dict]:
        """OCR识别字幕"""
        ocr = self._get_ocr_engine()
        ocr_config = self.config.get_ocr_config()

        raw_subtitles = []
        interval = self.config.get('ocr.frame_interval', 1)
        min_length = self.config.get('subtitle.min_length', 2)
        score_threshold = ocr_config.get('rec_score_thresh', 0.5)
        clean_pattern = re.compile(r'[\s\d\.\-\:\,\;\!\?\(\)\[\]\/\\]+')

        total_frames = len(frames)

        for i, frame_path in enumerate(frames):
            if self.cancel_requested:
                break

            frame_idx = int(os.path.basename(frame_path).replace("frame_", "").replace(".jpg", ""))
            timestamp = frame_idx * interval

            try:
                result = ocr.ocr(frame_path, cls=False)
                if result and result[0]:
                    texts = []
                    for line in result[0]:
                        text = line[1][0]
                        score = line[1][1]
                        if score >= score_threshold:
                            cleaned = clean_pattern.sub('', text)
                            if len(cleaned) >= min_length:
                                texts.append(text.strip())

                    if texts:
                        raw_subtitles.append({
                            'frame_idx': frame_idx,
                            'timestamp': timestamp,
                            'texts': texts
                        })

                if (i + 1) % 50 == 0 or (i + 1) == total_frames:
                    progress = (i + 1) / total_frames * 100
                    self._report_progress(2, 6, progress, f"OCR识别中... {i+1}/{total_frames}")

            except Exception:
                continue

        return raw_subtitles

    def _text_similarity(self, t1: str, t2: str) -> float:
        """计算文本相似度"""
        if not t1 or not t2:
            return 0.0
        set1, set2 = set(t1), set(t2)
        intersection = set1 & set2
        union = set1 | set2
        return len(intersection) / len(union) if union else 0.0

    def _organize_subtitles(self, raw_subtitles: List[Dict]) -> List[SubtitleItem]:
        """整理字幕"""
        if not raw_subtitles:
            return []

        sub_config = self.config.get('subtitle', {})
        max_gap = sub_config.get('max_gap', 3.0)
        max_duration = sub_config.get('max_duration', 30.0)
        threshold = sub_config.get('similarity_threshold', 0.8)
        interval = self.config.get('ocr.frame_interval', 1)

        merged = []
        current_text = raw_subtitles[0]['texts']
        current_start = raw_subtitles[0]['timestamp']
        current_end = raw_subtitles[0]['timestamp'] + interval

        for i in range(1, len(raw_subtitles)):
            item = raw_subtitles[i]
            text_str = " ".join(item['texts'])
            similarity = self._text_similarity(" ".join(current_text), text_str)
            gap = item['timestamp'] - current_end

            if similarity >= threshold and gap <= max_gap:
                current_text = item['texts']
                current_end = item['timestamp'] + interval
            else:
                merged.append(SubtitleItem(
                    start=current_start,
                    end=current_end,
                    text=" ".join(current_text)
                ))
                current_text = item['texts']
                current_start = item['timestamp']
                current_end = item['timestamp'] + interval

        merged.append(SubtitleItem(
            start=current_start,
            end=current_end,
            text=" ".join(current_text)
        ))

        final_subs = []
        for sub in merged:
            duration = sub.end - sub.start
            if duration > max_duration:
                num_parts = int(duration / max_duration) + 1
                part_duration = duration / num_parts
                for j in range(num_parts):
                    final_subs.append(SubtitleItem(
                        start=sub.start + j * part_duration,
                        end=sub.start + (j + 1) * part_duration,
                        text=sub.text
                    ))
            else:
                final_subs.append(sub)

        return final_subs

    def _translate_subtitles(self, subtitles: List[SubtitleItem]) -> List[SubtitleItem]:
        """翻译字幕（使用批量翻译优化）"""
        if not self.translator:
            return subtitles

        untranslated = [sub for sub in subtitles if not sub.translation]
        total = len(untranslated)
        
        if total == 0:
            return subtitles

        batch_size = 10
        num_batches = (total + batch_size - 1) // batch_size
        
        for batch_idx in range(0, num_batches):
            if self.cancel_requested:
                break

            batch_start = batch_idx * batch_size
            batch_end = min(batch_start + batch_size, total)
            batch = untranslated[batch_start:batch_end]
            texts = [sub.text for sub in batch]

            translations = self.translator.translate_batch(texts)
            
            for sub, trans in zip(batch, translations):
                if trans:
                    sub.translation = trans

            if (batch_idx + 1) % 10 == 0 or batch_idx == num_batches - 1:
                progress = batch_end / total * 100
                self._report_progress(4, 6, progress, f"翻译中... {batch_end}/{total}")

        return subtitles

    def _format_timestamp_srt(self, seconds: float) -> str:
        """格式化SRT时间戳"""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        millis = int((td.total_seconds() % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _save_srt(self, subtitles: List[SubtitleItem], output_path: str):
        """保存SRT文件"""
        with open(output_path, "w", encoding="utf-8-sig") as f:
            for i, sub in enumerate(subtitles, 1):
                start_ts = self._format_timestamp_srt(sub.start)
                end_ts = self._format_timestamp_srt(sub.end)
                f.write(f"{i}\n")
                f.write(f"{start_ts} --> {end_ts}\n")
                f.write(f"{sub.text}\n")
                if sub.translation:
                    f.write(f"{sub.translation}\n")
                f.write("\n")

    def _format_timestamp_ass(self, seconds: float) -> str:
        """格式化ASS时间戳"""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        centis = int((td.total_seconds() % 1) * 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"

    def _generate_ass(self, subtitles: List[SubtitleItem], output_path: str, video_info: Dict):
        """生成ASS字幕文件"""
        style_config = self.config.get_ass_config()
        width = video_info['width']
        height = video_info['height']

        ass_content = f"""[Script Info]
Title: Japanese Subtitle Translation
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{style_config.get('font_name', 'Microsoft YaHei')},{style_config.get('font_size', 20)},{style_config.get('primary_color', '&H00FFFFFF')},&H000000FF,{style_config.get('outline_color', '&H00000000')},&H80000000,-1,0,0,0,100,100,0,0,1,{style_config.get('outline_width', 2)},{style_config.get('shadow', 1)},2,10,10,{style_config.get('margin_v', 30)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        for sub in subtitles:
            start = self._format_timestamp_ass(sub.start)
            end = self._format_timestamp_ass(sub.end)

            text_line = sub.text.replace("\n", " ")
            if sub.translation:
                trans_line = sub.translation.replace("\n", " ")
                ass_text = f"{text_line}\\N{trans_line}"
            else:
                ass_text = text_line

            ass_text = ass_text.replace("{", "\\{").replace("}", "\\}")
            ass_content += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{ass_text}\n"

        with open(output_path, "w", encoding="utf-8-sig") as f:
            f.write(ass_content)

    def _burn_subtitles(self, video_path: str, ass_path: str, output_path: str) -> tuple[bool, str]:
        """烧录字幕到视频，返回 (成功, 错误信息)"""
        import logging
        logger = logging.getLogger(__name__)
        
        ffmpeg = self.config.get('paths.ffmpeg_path', 'ffmpeg')
        burn_config = self.config.get_burn_config()

        test_cmd = [ffmpeg, "-hide_banner", "-encoders"]
        try:
            result = subprocess.run(test_cmd, capture_output=True, encoding='utf-8', errors='ignore', timeout=10, startupinfo=_SUBPROCESS_STARTUPINFO)
            has_nvenc = "h264_nvenc" in result.stdout
        except Exception as e:
            logger.warning(f"检测NVENC失败: {e}，使用libx264")
            has_nvenc = False

        video_path_abs = os.path.abspath(video_path)
        ass_path_abs = os.path.abspath(ass_path)
        output_path_abs = os.path.abspath(output_path)

        logger.info(f"视频路径: {video_path_abs}")
        logger.info(f"ASS路径: {ass_path_abs}")
        logger.info(f"输出路径: {output_path_abs}")
        
        print(f"[DEBUG] 视频路径: {video_path_abs}")
        print(f"[DEBUG] ASS路径: {ass_path_abs}")
        print(f"[DEBUG] 输出路径: {output_path_abs}")
        
        if not os.path.exists(video_path_abs):
            error_msg = f"视频文件不存在: {video_path_abs}"
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}")
            return False, error_msg
            
        if not os.path.exists(ass_path_abs):
            error_msg = f"ASS字幕文件不存在: {ass_path_abs}"
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}")
            return False, error_msg

        output_dir = os.path.dirname(output_path_abs)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                logger.info(f"创建输出目录: {output_dir}")
            except Exception as e:
                error_msg = f"创建输出目录失败: {e}"
                logger.error(error_msg)
                return False, error_msg

        temp_ass = None
        main_output_dir = self.config.get('paths.output_dir', '')
        try:
            temp_dir_setting = self.config.get('processing.temp_dir', '')
            if temp_dir_setting:
                temp_dir = temp_dir_setting
            else:
                temp_dir = os.path.join(main_output_dir, "temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            temp_ass = os.path.join(temp_dir, "temp_sub.ass")
            import shutil
            shutil.copy2(ass_path_abs, temp_ass)
            
            ass_escaped = temp_ass.replace("\\", "/")
            if ass_escaped[1:2] == ":":
                ass_escaped = ass_escaped[0] + "\\\\:" + ass_escaped[2:]
        except Exception as e:
            logger.warning(f"创建临时字幕文件失败: {e}，尝试直接使用")
            ass_escaped = ass_path_abs.replace("\\", "/")
            if ass_escaped[1:2] == ":":
                ass_escaped = ass_escaped[0] + "\\\\:" + ass_escaped[2:]

        if has_nvenc:
            cmd = [ffmpeg, "-y", "-i", video_path_abs,
                   "-vf", f"ass={ass_escaped}",
                   "-c:v", "h264_nvenc",
                   "-preset", burn_config.get('preset', 'p4'),
                   "-rc", "constqp",
                   "-qp", str(burn_config.get('crf', 23)),
                   "-c:a", "copy",
                   output_path_abs]
            logger.info(f"使用NVENC编码器烧录字幕")
        else:
            cmd = [ffmpeg, "-y", "-i", video_path_abs,
                   "-vf", f"ass={ass_escaped}",
                   "-c:v", "libx264",
                   "-preset", "medium",
                   "-crf", str(burn_config.get('crf', 23)),
                   "-c:a", "copy",
                   output_path_abs]
            logger.info(f"使用libx264编码器烧录字幕")

        logger.info(f"FFmpeg命令: {' '.join(cmd)}")
        print(f"[DEBUG] FFmpeg命令: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='ignore', timeout=7200, startupinfo=_SUBPROCESS_STARTUPINFO)
            print(f"[DEBUG] FFmpeg返回码: {result.returncode}")
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "未知错误"
                logger.error(f"FFmpeg 烧录错误: {error_msg}")
                print(f"[ERROR] FFmpeg错误: {error_msg}")
                if temp_ass and os.path.exists(temp_ass):
                    try:
                        os.remove(temp_ass)
                    except:
                        pass
                if result.stdout:
                    logger.error(f"FFmpeg 输出: {result.stdout}")
                    print(f"[DEBUG] FFmpeg输出: {result.stdout}")
                return False, error_msg[:200]
            if temp_ass and os.path.exists(temp_ass):
                try:
                    os.remove(temp_ass)
                except:
                    pass
            if not os.path.exists(output_path_abs):
                return False, "输出文件未创建"
            return True, ""
        except subprocess.TimeoutExpired:
            if temp_ass and os.path.exists(temp_ass):
                try:
                    os.remove(temp_ass)
                except:
                    pass
            error_msg = "字幕烧录超时（2小时）"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            if temp_ass and os.path.exists(temp_ass):
                try:
                    os.remove(temp_ass)
                except:
                    pass
            error_msg = f"字幕烧录异常: {e}"
            logger.error(error_msg)
            return False, error_msg

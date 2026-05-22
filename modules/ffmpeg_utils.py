"""
FFmpeg 工具模块
封装 FFmpeg 和 ffprobe 的调用，支持相对路径自动解析
"""

import os
import subprocess
import json
from typing import Dict, Any, Optional, Tuple
from .logger import logger


class FFmpegUtils:
    """FFmpeg 工具类"""
    
    def __init__(self, ffmpeg_path: str = "./bin/ffmpeg.exe", ffprobe_path: str = "./bin/ffprobe.exe"):
        self.ffmpeg_path = self._resolve_path(ffmpeg_path)
        self.ffprobe_path = self._resolve_path(ffprobe_path)
        self._validate_tools()
    
    def _resolve_path(self, path: str) -> str:
        """解析工具路径：若为相对路径则基于程序根目录转换为绝对路径"""
        if not path:
            return path
        if os.path.isabs(path):
            return path
        from .config_manager import get_base_dir
        base_dir = get_base_dir()
        return os.path.normpath(os.path.join(base_dir, path))
    
    def _validate_tools(self):
        """验证 FFmpeg 和 ffprobe 是否可用"""
        if not self._is_executable(self.ffmpeg_path):
            logger.warning(f"FFmpeg 不可用: {self.ffmpeg_path}")
        
        if not self._is_executable(self.ffprobe_path):
            logger.warning(f"ffprobe 不可用: {self.ffprobe_path}")
    
    def _is_executable(self, path: str) -> bool:
        """检查路径是否为可执行文件"""
        if not path:
            return False
        if os.path.exists(path) and os.access(path, os.X_OK):
            return True
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                timeout=10,
                startupinfo=self._get_startupinfo()
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_startupinfo(self):
        """获取隐藏控制台窗口的 startupinfo（仅 Windows）"""
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            return startupinfo
        return None
    
    def get_video_info(self, video_path: str) -> Optional[Dict[str, Any]]:
        """获取视频信息"""
        try:
            cmd = [
                self.ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_streams",
                "-show_format",
                video_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                startupinfo=self._get_startupinfo()
            )
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                return info
            
            logger.error(f"获取视频信息失败: {result.stderr}")
            return None
            
        except Exception as e:
            logger.exception(f"获取视频信息异常: {video_path}")
            return None
    
    def get_video_duration(self, video_path: str) -> float:
        """获取视频时长（秒）"""
        info = self.get_video_info(video_path)
        if info:
            duration = info.get('format', {}).get('duration')
            if duration:
                return float(duration)
        return 0.0
    
    def extract_frames(self, video_path: str, output_dir: str, interval: int = 1,
                       quality: int = 2) -> bool:
        """提取视频帧"""
        os.makedirs(output_dir, exist_ok=True)
        
        frame_pattern = os.path.join(output_dir, "frame_%06d.jpg")
        
        cmd = [
            self.ffmpeg_path,
            "-i", video_path,
            "-vf", f"fps=1/{interval}",
            "-q:v", str(quality),
            "-start_number", "0",
            frame_pattern
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
                startupinfo=self._get_startupinfo()
            )
            
            if result.returncode == 0:
                logger.info(f"帧提取成功: {video_path} -> {output_dir}")
                return True
            
            logger.error(f"帧提取失败: {result.stderr}")
            return False
            
        except Exception as e:
            logger.exception(f"帧提取异常: {video_path}")
            return False
    
    def burn_subtitles(self, video_path: str, ass_path: str, output_path: str,
                       preset: str = "p4", crf: int = 23) -> Tuple[bool, str]:
        """烧录字幕到视频"""
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-i", ass_path,
                "-c:v", "h264_nvenc",
                "-preset", preset,
                "-crf", str(crf),
                "-c:a", "copy",
                "-map", "0:v:0",
                "-map", "0:a?",
                "-map", "1:s:0",
                "-y",
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800,
                startupinfo=self._get_startupinfo()
            )
            
            if result.returncode == 0:
                logger.info(f"字幕烧录成功: {video_path} -> {output_path}")
                return True, ""
            
            error_msg = result.stderr or result.stdout
            logger.error(f"字幕烧录失败: {error_msg}")
            return False, error_msg
            
        except Exception as e:
            logger.exception(f"字幕烧录异常: {video_path}")
            return False, str(e)
    
    def check_ffmpeg(self) -> Tuple[bool, str]:
        """检查 FFmpeg 是否可用"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=10,
                startupinfo=self._get_startupinfo()
            )
            
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                logger.info(f"FFmpeg 版本: {version_line}")
                return True, version_line
            
            return False, f"FFmpeg 执行失败: {result.stderr}"
            
        except FileNotFoundError:
            return False, "FFmpeg 未找到，请检查路径配置"
        except Exception as e:
            return False, f"FFmpeg 检查异常: {str(e)}"
    
    def generate_ass(self, subtitles: list, output_path: str, video_info: dict,
                     style_config: dict) -> bool:
        """生成 ASS 字幕文件"""
        try:
            font_name = style_config.get('font_name', 'Microsoft YaHei')
            font_size = style_config.get('font_size', 20)
            primary_color = style_config.get('primary_color', '&H00FFFFFF')
            outline_color = style_config.get('outline_color', '&H00000000')
            outline_width = style_config.get('outline_width', 2)
            shadow = style_config.get('shadow', 1)
            margin_v = style_config.get('margin_v', 30)
            
            video_width = video_info.get('width', 1920)
            video_height = video_info.get('height', 1080)
            
            ass_content = f"""[Script Info]
Title: AVT Subtitle
ScriptType: v4.00+
Collisions: Normal
PlayResX: {video_width}
PlayResY: {video_height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{primary_color},&H00000000,{outline_color},&H00000000,0,0,0,0,100,100,0,0,1,{outline_width},{shadow},2,10,10,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
            
            for sub in subtitles:
                start_time = self._format_time(sub['start'])
                end_time = self._format_time(sub['end'])
                text = self._escape_ass_text(sub.get('translated', sub.get('text', '')))
                ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n"
            
            with open(output_path, 'w', encoding='utf-8-sig') as f:
                f.write(ass_content)
            
            logger.info(f"ASS 字幕生成成功: {output_path}")
            return True
            
        except Exception as e:
            logger.exception(f"ASS 字幕生成异常: {output_path}")
            return False
    
    def _format_time(self, seconds: float) -> str:
        """将秒转换为 ASS 时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centis = int((seconds - int(seconds)) * 100)
        return f"{hours:d}:{minutes:02d}:{secs:02d}.{centis:02d}"
    
    def _escape_ass_text(self, text: str) -> str:
        """转义 ASS 文本中的特殊字符"""
        text = text.replace("\\", "\\\\")
        text = text.replace("{", "\\{")
        text = text.replace("}", "\\}")
        text = text.replace("[", "\\[")
        text = text.replace("]", "\\]")
        text = text.replace(";", "\\;")
        text = text.replace(",", "\\,")
        return text

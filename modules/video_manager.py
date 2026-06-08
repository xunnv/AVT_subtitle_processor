"""
视频管理器模块
负责视频文件的扫描、状态管理和队列处理
"""

import os
from typing import List, Dict, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


class VideoStatus(Enum):
    """视频处理状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class VideoInfo:
    """视频信息数据类"""
    path: str
    name: str
    size: int
    mtime: float = 0.0
    ctime: float = 0.0
    duration: Optional[float] = None
    resolution: Optional[str] = None
    status: VideoStatus = VideoStatus.PENDING
    progress: float = 0.0
    current_step: str = ""
    error_message: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    output_path: Optional[str] = None
    subtitle_path: Optional[str] = None
    hash: str = ""

    def __post_init__(self):
        if not self.hash and self.path:
            self.hash = hashlib.md5(self.path.encode()).hexdigest()[:8]

    @property
    def duration_str(self) -> str:
        """返回格式化时长"""
        if self.duration:
            mins = int(self.duration // 60)
            secs = int(self.duration % 60)
            return f"{mins}:{secs:02d}"
        return "--:--"

    @property
    def size_str(self) -> str:
        """返回格式化大小"""
        mb = self.size / (1024 * 1024)
        if mb >= 1024:
            return f"{mb/1024:.1f} GB"
        return f"{mb:.1f} MB"

    @property
    def status_text(self) -> str:
        """返回状态的中文显示文本"""
        status_map = {
            VideoStatus.PENDING: "待处理",
            VideoStatus.PROCESSING: "处理中",
            VideoStatus.COMPLETED: "已完成",
            VideoStatus.FAILED: "失败",
            VideoStatus.SKIPPED: "已跳过"
        }
        return status_map.get(self.status, "未知")

    @property
    def processing_time(self) -> Optional[float]:
        """返回处理耗时（秒）"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return None

    @property
    def processing_time_str(self) -> str:
        """返回格式化处理时间"""
        elapsed = self.processing_time
        if elapsed:
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            return f"{mins}分{secs}秒"
        return "--"


class VideoManager:
    """视频管理器类"""

    def __init__(self, config_manager):
        self.config = config_manager
        self.videos: List[VideoInfo] = []
        self.current_index: int = -1
        self._scan_directory()

    def _scan_directory(self, sort_by: str = 'name', reverse: bool = False):
        """扫描输入目录中的视频文件"""
        input_dir = self.config.get('paths.video_input', '')
        if not os.path.exists(input_dir):
            return

        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv']
        video_files = []

        for file in os.listdir(input_dir):
            ext = os.path.splitext(file)[1].lower()
            if ext in video_extensions:
                full_path = os.path.join(input_dir, file)
                video_files.append(full_path)

        videos = [self._create_video_info(path) for path in video_files]
        self.videos = self._sort_videos(videos, sort_by, reverse)

    def _sort_videos(self, videos: list, sort_by: str = 'name', reverse: bool = False) -> list:
        """排序视频列表"""
        sort_key_map = {
            'name': lambda v: v.name.lower(),
            'size': lambda v: v.size,
            'mtime': lambda v: v.mtime,
            'ctime': lambda v: v.ctime
        }

        sort_key = sort_key_map.get(sort_by, lambda v: v.name.lower())
        return sorted(videos, key=sort_key, reverse=reverse)

    def sort_videos(self, sort_by: str = 'name', reverse: bool = False):
        """排序现有视频列表"""
        self.videos = self._sort_videos(self.videos, sort_by, reverse)

    def rescan(self, sort_by: str = 'name', reverse: bool = False):
        """重新扫描目录"""
        self._scan_directory(sort_by, reverse)

    def _create_video_info(self, path: str) -> VideoInfo:
        """创建视频信息对象"""
        name = os.path.basename(path)
        size = os.path.getsize(path)
        stat = os.stat(path)

        video_info = VideoInfo(
            path=path,
            name=name,
            size=size,
            mtime=stat.st_mtime,
            ctime=stat.st_ctime,
            status=VideoStatus.PENDING
        )

        if self._is_processed(path):
            video_info.status = VideoStatus.COMPLETED
            video_info.progress = 100.0

        return video_info

    def _is_processed(self, video_path: str) -> bool:
        """检查视频是否已处理"""
        output_dir = self.config.get('paths.output_dir', '')
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        output_video = os.path.join(output_dir, "videos", f"{video_name}_subtitled.mp4")
        return os.path.exists(output_video)

    def add_video(self, path: str) -> bool:
        """添加单个视频"""
        if not os.path.exists(path):
            return False

        # 检查是否已存在
        if any(v.path == path for v in self.videos):
            return False

        video_info = self._create_video_info(path)
        self.videos.append(video_info)
        return True

    def add_videos(self, paths: List[str]) -> int:
        """批量添加视频"""
        added = 0
        for path in paths:
            if self.add_video(path):
                added += 1
        return added

    def remove_video(self, index: int) -> bool:
        """移除视频"""
        if 0 <= index < len(self.videos):
            self.videos.pop(index)
            return True
        return False

    def clear_videos(self):
        """清空视频列表"""
        self.videos.clear()
        self.current_index = -1

    def get_videos(self) -> List[VideoInfo]:
        """获取所有视频列表"""
        return self.videos

    def get_pending_videos(self) -> List[VideoInfo]:
        """获取待处理的视频列表"""
        return [v for v in self.videos if v.status == VideoStatus.PENDING]

    def get_current_video(self) -> Optional[VideoInfo]:
        """获取当前处理的视频"""
        if 0 <= self.current_index < len(self.videos):
            return self.videos[self.current_index]
        return None

    def set_current(self, index: int) -> bool:
        """设置当前处理索引"""
        if 0 <= index < len(self.videos):
            self.current_index = index
            return True
        return False

    def next_video(self) -> Optional[VideoInfo]:
        """获取下一个待处理的视频"""
        pending = self.get_pending_videos()
        if pending:
            return pending[0]
        return None

    def update_status(self, index: int, status: VideoStatus,
                     progress: float = None, step: str = None,
                     error: str = None):
        """更新视频状态"""
        if 0 <= index < len(self.videos):
            video = self.videos[index]
            video.status = status

            if progress is not None:
                video.progress = progress
            if step:
                video.current_step = step
            if error:
                video.error_message = error

            if status == VideoStatus.PROCESSING and not video.start_time:
                video.start_time = datetime.now()
            elif status in [VideoStatus.COMPLETED, VideoStatus.FAILED]:
                video.end_time = datetime.now()

    def get_statistics(self) -> Dict[str, int]:
        """获取处理统计"""
        stats = {
            'total': len(self.videos),
            'pending': 0,
            'processing': 0,
            'completed': 0,
            'failed': 0,
            'skipped': 0
        }

        for video in self.videos:
            stats[video.status.value] += 1

        return stats

    def refresh(self):
        """刷新视频列表"""
        self._scan_directory()

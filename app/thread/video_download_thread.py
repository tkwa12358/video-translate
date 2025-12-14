import os
import re
from pathlib import Path

import requests
import yt_dlp
from PyQt5.QtCore import QThread, pyqtSignal

from app.common.config import cfg
from app.config import APPDATA_PATH
from app.core.entities import DownloadResolutionEnum, SubtitleDownloadTypeEnum
from app.core.utils.logger import setup_logger

logger = setup_logger("video_download_thread")


class VideoDownloadThread(QThread):
    """视频下载线程类"""

    finished = pyqtSignal(
        str
    )  # 发送下载完成的信号(视频路径, 字幕路径, 缩略图路径, 视频信息)
    progress = pyqtSignal(int, str)  # 发送下载进度的信号
    error = pyqtSignal(str)  # 发送错误信息的信号

    def __init__(self, url: str, work_dir: str):
        super().__init__()
        self.url = url
        self.work_dir = work_dir

    def run(self):
        try:
            video_file_path, subtitle_file_path, thumbnail_file_path, info_dict = (
                self.download()
            )
            self.finished.emit(video_file_path)
        except Exception as e:
            logger.exception("下载视频失败: %s", str(e))
            self.error.emit(str(e))

    def progress_hook(self, d):
        """下载进度回调函数"""
        if d["status"] == "downloading":
            percent = d["_percent_str"]
            speed = d["_speed_str"]

            # 提取百分比和速度的纯文本
            clean_percent = (
                percent.replace("\x1b[0;94m", "")
                .replace("\x1b[0m", "")
                .strip()
                .replace("%", "")
            )
            clean_speed = speed.replace("\x1b[0;32m", "").replace("\x1b[0m", "").strip()

            self.progress.emit(
                int(float(clean_percent)),
                f"下载进度: {clean_percent}%  速度: {clean_speed}",
            )

    def sanitize_filename(self, name: str, replacement: str = "_") -> str:
        """清理文件名中不允许的字符"""
        # 定义不允许的字符
        forbidden_chars = r'<>:"/\\|?*'

        # 替换不允许的字符
        sanitized = re.sub(f"[{re.escape(forbidden_chars)}]", replacement, name)

        # 移除控制字符
        sanitized = re.sub(r"[\0-\31]", "", sanitized)

        # 去除文件名末尾的空格和点
        sanitized = sanitized.rstrip(" .")

        # 限制文件名长度
        max_length = 255
        if len(sanitized) > max_length:
            base, ext = os.path.splitext(sanitized)
            base_max_length = max_length - len(ext)
            sanitized = base[:base_max_length] + ext

        # 处理Windows保留名称
        windows_reserved_names = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        }
        name_without_ext = os.path.splitext(sanitized)[0].upper()
        if name_without_ext in windows_reserved_names:
            sanitized = f"{sanitized}_"

        # 如果文件名为空，返回默认名称
        if not sanitized:
            sanitized = "default_filename"

        return sanitized

    def download(self, need_subtitle: bool = True, need_thumbnail: bool = False):
        """下载视频"""
        logger.info("开始下载视频: %s", self.url)

        # 获取分辨率配置
        resolution_map = {
            DownloadResolutionEnum.P360: "bestvideo[height<=360]+bestaudio/best[height<=360]/best",
            DownloadResolutionEnum.P480: "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
            DownloadResolutionEnum.P720: "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
            DownloadResolutionEnum.P1080: "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
            DownloadResolutionEnum.P4K: "bestvideo+bestaudio/best",
        }
        format_str = resolution_map.get(
            cfg.download_resolution.value, "bestvideo+bestaudio/best"
        )

        # 获取字幕配置
        sub_type = cfg.subtitle_download_type.value
        write_sub = False
        write_auto_sub = False

        if sub_type == SubtitleDownloadTypeEnum.OFFICIAL_ONLY:
            write_sub = True
            write_auto_sub = False
        elif sub_type == SubtitleDownloadTypeEnum.OFFICIAL_PREFERRED:
            write_sub = True
            write_auto_sub = True
        elif sub_type == SubtitleDownloadTypeEnum.AUTO:
            write_sub = False
            write_auto_sub = True
        elif sub_type == SubtitleDownloadTypeEnum.NONE:
            write_sub = False
            write_auto_sub = False

        # 初始化 ydl 选项
        initial_ydl_opts = {
            "outtmpl": {
                "default": "%(title).200s.%(ext)s",  # 限制文件名最长200个字符
                "subtitle": "【下载字幕】.%(ext)s",
                "thumbnail": "thumbnail",
            },
            "format": format_str,
            "progress_hooks": [self.progress_hook],  # 下载进度钩子
            "quiet": True,  # 禁用日志输出
            "no_warnings": True,  # 禁用警告信息
            "noprogress": True,
            "writesub": write_sub,
            "writeautomaticsub": write_auto_sub,
            "writethumbnail": need_thumbnail,  # 下载缩略图
            "thumbnail_format": "jpg",  # 指定缩略图的格式
        }

        # 检查 cookies 文件 (仅当配置开启时)
        if cfg.use_cookie_file.value:
            cookiefile_path = APPDATA_PATH / "cookies.txt"
            if cookiefile_path.exists():
                logger.info(f"使用cookiefile: {cookiefile_path}")
                initial_ydl_opts["cookiefile"] = str(cookiefile_path)

        with yt_dlp.YoutubeDL(initial_ydl_opts) as ydl:
            # 提取视频信息（不下载）
            info_dict = ydl.extract_info(self.url, download=False)

            # 设置动态下载文件夹为视频标题 (结构: work_dir/videocap/title)
            video_title = self.sanitize_filename(info_dict.get("title", "MyVideo"))
            video_work_dir = (
                Path(self.work_dir) / "videocap" / self.sanitize_filename(video_title)
            )
            subtitle_language = info_dict.get("language", None)
            if subtitle_language:
                subtitle_language = subtitle_language.lower().split("-")[0]

            try:
                subtitle_download_link = None
                automatic_captions = info_dict.get("automatic_captions")
                if automatic_captions and subtitle_language:
                    for lang_code in automatic_captions:
                        if lang_code.startswith(subtitle_language):
                            subtitle_download_link = automatic_captions[lang_code][-1][
                                "url"
                            ]
                            break
            except Exception:
                subtitle_download_link = None

            # 设置 yt-dlp 下载选项
            ydl_opts = {
                "paths": {
                    "home": str(video_work_dir),
                    "subtitle": str(video_work_dir / "subtitle"),
                    "thumbnail": str(video_work_dir),
                },
            }
            # 更新 yt-dlp 的配置
            ydl.params.update(ydl_opts)

            # 使用 process_info 进行下载
            ydl.process_info(info_dict)

            # 获取视频文件路径
            video_file_path = Path(ydl.prepare_filename(info_dict))
            if video_file_path.exists():
                video_file_path = str(video_file_path)
            else:
                video_file_path = None

            # 获取字幕文件路径
            subtitle_file_path = None
            for file in video_work_dir.glob("**/【下载字幕】*"):
                file_path = str(file)
                if subtitle_language and subtitle_language not in file_path:
                    logger.info(
                        "字幕语言错误，重新下载字幕: %s", subtitle_download_link
                    )
                    os.remove(file_path)
                    if subtitle_download_link:
                        response = requests.get(subtitle_download_link)
                        file_path = (
                            video_work_dir
                            / "subtitle"
                            / f"【下载字幕】{subtitle_language}.vtt"
                        )
                        if res := response.text:
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(res)
                            subtitle_file_path = file_path
                else:
                    subtitle_file_path = file_path
                break

            # 获取缩略图文件路径
            thumbnail_file_path = None
            for file in video_work_dir.glob("**/thumbnail*"):
                thumbnail_file_path = str(file)
                break

            logger.info(f"视频下载完成: {video_file_path}")
            logger.info(f"字幕文件路径: {subtitle_file_path}")
            return video_file_path, subtitle_file_path, thumbnail_file_path, info_dict

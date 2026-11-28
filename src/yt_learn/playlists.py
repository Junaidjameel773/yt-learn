"""Resolve YouTube playlists and video metadata with yt-dlp."""

import logging
from dataclasses import dataclass
from datetime import date, datetime

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

log = logging.getLogger(__name__)

# Titles yt-dlp's flat extraction gives entries that cannot be watched.
_UNAVAILABLE_TITLES = {"[Private video]", "[Deleted video]"}


@dataclass(frozen=True)
class PlaylistVideo:
    video_id: str
    title: str
    duration: float | None  # seconds; None when YouTube does not report it


@dataclass(frozen=True)
class VideoInfo:
    video_id: str
    title: str
    channel: str
    duration: float | None  # seconds; None when YouTube does not report it
    published: date | None


class VideoUnavailable(Exception):
    """Metadata for a video could not be fetched (private, deleted, or blocked)."""

    def __init__(self, video_id: str, reason: str) -> None:
        super().__init__(f"Video {video_id} is unavailable: {reason}")
        self.video_id = video_id


def _extract(url: str, **opts) -> dict:
    with YoutubeDL({"skip_download": True, "quiet": True, **opts}) as ydl:
        return ydl.extract_info(url, download=False)


def resolve_playlist(playlist_id: str) -> list[PlaylistVideo]:
    """Return the playlist's videos in order. Nothing is downloaded.

    Private and deleted entries are skipped and logged.
    """
    url = f"https://www.youtube.com/playlist?list={playlist_id}"
    info = _extract(url, extract_flat="in_playlist")

    videos = []
    for entry in info.get("entries") or []:
        if not entry or not entry.get("id") or entry.get("title") in _UNAVAILABLE_TITLES:
            log.info("Skipping unavailable entry in playlist %s: %r", playlist_id, entry)
            continue
        videos.append(PlaylistVideo(entry["id"], entry.get("title") or "", entry.get("duration")))
    return videos


def get_video_info(video_id: str) -> VideoInfo:
    """Return title, channel, duration, and publish date of a video. Nothing is downloaded.

    Raises VideoUnavailable when yt-dlp cannot extract the video.
    """
    try:
        info = _extract(f"https://www.youtube.com/watch?v={video_id}")
    except DownloadError as exc:
        raise VideoUnavailable(video_id, str(exc)) from exc

    upload_date = info.get("upload_date")  # "YYYYMMDD"
    return VideoInfo(
        video_id=video_id,
        title=info.get("title") or "",
        channel=info.get("channel") or info.get("uploader") or "",
        duration=info.get("duration"),
        published=datetime.strptime(upload_date, "%Y%m%d").date() if upload_date else None,
    )

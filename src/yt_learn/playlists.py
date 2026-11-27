"""Resolve YouTube playlists to their videos."""

import logging
from dataclasses import dataclass

from yt_dlp import YoutubeDL

log = logging.getLogger(__name__)

# Titles yt-dlp's flat extraction gives entries that cannot be watched.
_UNAVAILABLE_TITLES = {"[Private video]", "[Deleted video]"}


@dataclass(frozen=True)
class PlaylistVideo:
    video_id: str
    title: str
    duration: float | None  # seconds; None when YouTube does not report it


def resolve_playlist(playlist_id: str) -> list[PlaylistVideo]:
    """Return the playlist's videos in order. Nothing is downloaded.

    Private and deleted entries are skipped and logged.
    """
    url = f"https://www.youtube.com/playlist?list={playlist_id}"
    opts = {"extract_flat": "in_playlist", "skip_download": True, "quiet": True}
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    videos = []
    for entry in info.get("entries") or []:
        if not entry or not entry.get("id") or entry.get("title") in _UNAVAILABLE_TITLES:
            log.info("Skipping unavailable entry in playlist %s: %r", playlist_id, entry)
            continue
        videos.append(PlaylistVideo(entry["id"], entry.get("title") or "", entry.get("duration")))
    return videos

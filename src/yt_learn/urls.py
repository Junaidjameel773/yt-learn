"""Parse YouTube video and playlist URLs."""

import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

_YOUTUBE_HOSTS = {"youtube.com", "m.youtube.com", "music.youtube.com", "youtube-nocookie.com"}
_VIDEO_ID = re.compile(r"[A-Za-z0-9_-]{11}")
_PLAYLIST_ID = re.compile(r"[A-Za-z0-9_-]+")


@dataclass(frozen=True)
class YouTubeRef:
    video_id: str | None
    playlist_id: str | None


def parse_youtube_url(url: str) -> YouTubeRef:
    """Return the video and/or playlist ID in a YouTube URL.

    Raises ValueError for non-YouTube or malformed URLs.
    """
    url = url.strip()
    if "://" not in url:
        url = "https://" + url
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Not a YouTube URL: {url!r}")
    host = (parsed.hostname or "").removeprefix("www.")
    query = parse_qs(parsed.query)
    parts = [p for p in parsed.path.split("/") if p]

    video_id = None
    if host == "youtu.be":
        video_id = parts[0] if parts else None
    elif host in _YOUTUBE_HOSTS:
        if parts == ["watch"]:
            video_id = query.get("v", [None])[0]
        elif len(parts) >= 2 and parts[0] in ("shorts", "embed", "live", "v"):
            video_id = parts[1]
        elif parts != ["playlist"]:
            raise ValueError(f"Unsupported YouTube URL: {url!r}")
    else:
        raise ValueError(f"Not a YouTube URL: {url!r}")

    playlist_id = query.get("list", [None])[0]

    if video_id is not None and not _VIDEO_ID.fullmatch(video_id):
        raise ValueError(f"Invalid video ID in URL: {url!r}")
    if playlist_id is not None and not _PLAYLIST_ID.fullmatch(playlist_id):
        raise ValueError(f"Invalid playlist ID in URL: {url!r}")
    if video_id is None and playlist_id is None:
        raise ValueError(f"No video or playlist ID in URL: {url!r}")
    return YouTubeRef(video_id=video_id, playlist_id=playlist_id)

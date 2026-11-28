"""Fetch YouTube video transcripts."""

import json
import logging
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

from youtube_transcript_api import CouldNotRetrieveTranscript, YouTubeTranscriptApi

from yt_learn.config import get_settings

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Segment:
    text: str
    start: float
    duration: float


class TranscriptUnavailable(Exception):
    """No transcript could be fetched for a video."""

    def __init__(self, video_id: str, reason: str) -> None:
        super().__init__(f"No transcript available for video {video_id}: {reason}")
        self.video_id = video_id


def fetch_transcript(video_id: str, languages: Iterable[str] | None = None) -> list[Segment]:
    """Return the transcript of a video as a list of segments.

    `languages` is tried in order (default: the `TRANSCRIPT_LANGUAGES` setting). For each
    language a manually created transcript is preferred, then auto-generated captions.
    Results are cached as JSON under `DATA_DIR/transcripts/<video_id>.json` and reused
    when the same languages are requested again.
    Raises TranscriptUnavailable when nothing matches or YouTube refuses the request.
    """
    settings = get_settings()
    langs = list(languages or settings.transcript_languages)
    cache_file = settings.data_dir / "transcripts" / f"{video_id}.json"

    cached = _read_cache(cache_file, langs)
    if cached is not None:
        return cached

    try:
        fetched = YouTubeTranscriptApi().fetch(video_id, languages=langs)
    except CouldNotRetrieveTranscript as exc:
        reason = type(exc).__name__
        raise TranscriptUnavailable(video_id, reason) from exc
    segments = [Segment(s.text, s.start, s.duration) for s in fetched.snippets]

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    data = {"languages": langs, "segments": [asdict(s) for s in segments]}
    cache_file.write_text(json.dumps(data), encoding="utf-8")
    return segments


def _read_cache(path: Path, languages: list[str]) -> list[Segment] | None:
    """Return cached segments, or None if missing, corrupt, or fetched for other languages."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["languages"] != languages:
            return None
        return [Segment(**s) for s in data["segments"]]
    except FileNotFoundError:
        return None
    except (ValueError, KeyError, TypeError) as exc:
        log.warning("Ignoring corrupt transcript cache %s: %s", path, exc)
        return None

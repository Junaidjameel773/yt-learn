"""Fetch YouTube video transcripts."""

from collections.abc import Iterable
from dataclasses import dataclass

from youtube_transcript_api import CouldNotRetrieveTranscript, YouTubeTranscriptApi

from yt_learn.config import get_settings


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
    Raises TranscriptUnavailable when nothing matches or YouTube refuses the request.
    """
    langs = list(languages or get_settings().transcript_languages)
    try:
        fetched = YouTubeTranscriptApi().fetch(video_id, languages=langs)
    except CouldNotRetrieveTranscript as exc:
        reason = type(exc).__name__
        raise TranscriptUnavailable(video_id, reason) from exc
    return [Segment(s.text, s.start, s.duration) for s in fetched.snippets]

from unittest.mock import patch

import pytest
from youtube_transcript_api import (
    FetchedTranscript,
    FetchedTranscriptSnippet,
    NoTranscriptFound,
    TranscriptsDisabled,
)

from yt_learn.transcripts import Segment, TranscriptUnavailable, fetch_transcript

VID = "dQw4w9WgXcQ"


def _fetched() -> FetchedTranscript:
    return FetchedTranscript(
        snippets=[
            FetchedTranscriptSnippet(text="hello", start=0.0, duration=1.5),
            FetchedTranscriptSnippet(text="world", start=1.5, duration=2.0),
        ],
        video_id=VID,
        language="English",
        language_code="en",
        is_generated=True,
    )


@patch("yt_learn.transcripts.YouTubeTranscriptApi")
def test_fetch_returns_segments(api) -> None:
    api.return_value.fetch.return_value = _fetched()
    assert fetch_transcript(VID, ["de", "en"]) == [
        Segment("hello", 0.0, 1.5),
        Segment("world", 1.5, 2.0),
    ]
    api.return_value.fetch.assert_called_once_with(VID, languages=["de", "en"])


@patch("yt_learn.transcripts.YouTubeTranscriptApi")
def test_default_languages_from_settings(api, monkeypatch: pytest.MonkeyPatch) -> None:
    from yt_learn.config import get_settings

    monkeypatch.setenv("TRANSCRIPT_LANGUAGES", '["fr", "en"]')
    get_settings.cache_clear()
    try:
        api.return_value.fetch.return_value = _fetched()
        fetch_transcript(VID)
    finally:
        get_settings.cache_clear()
    api.return_value.fetch.assert_called_once_with(VID, languages=["fr", "en"])


@pytest.mark.parametrize(
    "error",
    [NoTranscriptFound(VID, ["en"], None), TranscriptsDisabled(VID)],
)
@patch("yt_learn.transcripts.YouTubeTranscriptApi")
def test_no_transcript_raises_domain_error(api, error: Exception) -> None:
    api.return_value.fetch.side_effect = error
    with pytest.raises(TranscriptUnavailable, match=VID) as info:
        fetch_transcript(VID, ["en"])
    assert info.value.video_id == VID
    assert info.value.__cause__ is error

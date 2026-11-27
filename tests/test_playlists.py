import logging
from unittest.mock import patch

import pytest

from yt_learn.playlists import PlaylistVideo, resolve_playlist

PL = "PLx0sYbCqOb8TBPRdmBHs5Iftvv9TPboYG"

FLAT_INFO = {
    "_type": "playlist",
    "id": PL,
    "entries": [
        {"id": "aaaaaaaaaaa", "title": "Intro", "duration": 120.0},
        {"id": "bbbbbbbbbbb", "title": "[Private video]", "duration": None},
        {"id": "ccccccccccc", "title": "Part 2", "duration": None},
        {"id": "ddddddddddd", "title": "[Deleted video]", "duration": None},
        None,
        {"id": "eeeeeeeeeee", "title": "Outro", "duration": 60},
    ],
}


@patch("yt_learn.playlists.YoutubeDL")
def test_resolve_playlist(ydl_cls, caplog: pytest.LogCaptureFixture) -> None:
    ydl = ydl_cls.return_value.__enter__.return_value
    ydl.extract_info.return_value = FLAT_INFO

    with caplog.at_level(logging.INFO, logger="yt_learn.playlists"):
        videos = resolve_playlist(PL)

    assert videos == [
        PlaylistVideo("aaaaaaaaaaa", "Intro", 120.0),
        PlaylistVideo("ccccccccccc", "Part 2", None),
        PlaylistVideo("eeeeeeeeeee", "Outro", 60),
    ]
    assert len([r for r in caplog.records if "Skipping" in r.message]) == 3

    opts = ydl_cls.call_args.args[0]
    assert opts["extract_flat"] == "in_playlist"
    ydl.extract_info.assert_called_once_with(
        f"https://www.youtube.com/playlist?list={PL}", download=False
    )


@patch("yt_learn.playlists.YoutubeDL")
def test_empty_playlist(ydl_cls) -> None:
    ydl_cls.return_value.__enter__.return_value.extract_info.return_value = {"entries": []}
    assert resolve_playlist(PL) == []

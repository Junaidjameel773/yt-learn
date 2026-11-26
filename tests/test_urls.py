import pytest

from yt_learn.urls import YouTubeRef, parse_youtube_url

VID = "dQw4w9WgXcQ"
PL = "PLx0sYbCqOb8TBPRdmBHs5Iftvv9TPboYG"


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (f"https://www.youtube.com/watch?v={VID}", YouTubeRef(VID, None)),
        (f"https://youtube.com/watch?v={VID}&t=42s", YouTubeRef(VID, None)),
        (f"https://m.youtube.com/watch?v={VID}", YouTubeRef(VID, None)),
        (f"http://www.youtube.com/watch?v={VID}", YouTubeRef(VID, None)),
        (f"www.youtube.com/watch?v={VID}", YouTubeRef(VID, None)),
        (f"https://youtu.be/{VID}", YouTubeRef(VID, None)),
        (f"https://youtu.be/{VID}?t=10", YouTubeRef(VID, None)),
        (f"https://www.youtube.com/shorts/{VID}", YouTubeRef(VID, None)),
        (f"https://www.youtube.com/embed/{VID}", YouTubeRef(VID, None)),
        (f"https://www.youtube-nocookie.com/embed/{VID}", YouTubeRef(VID, None)),
        (f"https://www.youtube.com/playlist?list={PL}", YouTubeRef(None, PL)),
        (f"https://www.youtube.com/watch?v={VID}&list={PL}", YouTubeRef(VID, PL)),
        (f"https://youtu.be/{VID}?list={PL}", YouTubeRef(VID, PL)),
        (f"  https://youtu.be/{VID}  ", YouTubeRef(VID, None)),
    ],
)
def test_parse_valid(url: str, expected: YouTubeRef) -> None:
    assert parse_youtube_url(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "",
        "not a url",
        f"https://vimeo.com/watch?v={VID}",
        f"https://notyoutube.com/watch?v={VID}",
        f"ftp://youtube.com/watch?v={VID}",
        "https://www.youtube.com/watch",
        "https://www.youtube.com/watch?v=short",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ!!",
        "https://youtu.be/",
        "https://www.youtube.com/playlist",
        "https://www.youtube.com/playlist?list=bad%20id",
        "https://www.youtube.com/channel/UC123",
        "https://www.youtube.com/shorts/",
    ],
)
def test_parse_invalid(url: str) -> None:
    with pytest.raises(ValueError):
        parse_youtube_url(url)

from fastapi import FastAPI

from yt_learn import __version__

app = FastAPI(title="yt-learn", version=__version__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}

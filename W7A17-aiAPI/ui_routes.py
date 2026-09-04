from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

INDEX_PATH = Path(__file__).resolve().parent / "static" / "index.html"

router = APIRouter()


@router.get("/ui", include_in_schema=False, response_class=HTMLResponse)
def ui():
    return HTMLResponse(INDEX_PATH.read_text(encoding="utf-8"))

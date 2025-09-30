from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from .models import DigestRequest, DigestResponse, ArticleSummary
from .aggregator import aggregate_category
from .summarizer import TIME_MAP, summarize_article
from .tts import text_to_speech
from fastapi.responses import FileResponse
from pathlib import Path
import os

router = APIRouter()

@router.post("/api/digest", response_model=DigestResponse)
async def create_digest(req: DigestRequest):
    minutes = req.minutes
    category = req.category.lower()
    if minutes not in TIME_MAP:
        raise HTTPException(status_code=400, detail="Invalid minutes. Choose 5,10,20,30,60")

    cfg = TIME_MAP[minutes]
    articles = aggregate_category(category, refresh=False, max_articles=cfg["articles"]*2)
    if not articles:
        raise HTTPException(404, "No articles found for category")

    # sort by published date if available, otherwise keep order
    # select top N
    selected = articles[:cfg["articles"]]

    summaries = []
    combined_for_audio = []
    for a in selected:
        text = a.get("text","")
        # summarization max_tokens from cfg
        max_tokens = cfg["max_tokens"]
        summary = summarize_article(text, max_tokens=max_tokens)
        summaries.append(ArticleSummary(
            title=a.get("title",""),
            source=a.get("source",""),
            url=a.get("url",""),
            published=a.get("published",""),
            summary=summary
        ))
        combined_for_audio.append(f"{a.get('title','')}. {summary}")

    audio_url = None
    if req.audio:
        combined_text = "\n\n".join(combined_for_audio)
        audio_path = text_to_speech(combined_text, lang=req.language or "en")
        # return path as a URL path (frontend should fetch from /audio/{filename})
        audio_filename = os.path.basename(audio_path)
        audio_url = f"/audio/{audio_filename}"

    return DigestResponse(
        category=category,
        minutes=minutes,
        summaries=summaries,
        audio_url=audio_url
    )

# serve audio files
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
app_static = None

@router.get("/audio/{fname}")
def serve_audio(fname: str):
    base = Path(__file__).resolve().parents[1] / "data" / "audio"
    file_path = base / fname
    if not file_path.exists():
        raise HTTPException(404,"Audio not found")
    return FileResponse(str(file_path), media_type="audio/mpeg")
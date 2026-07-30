from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .files import extract_uploaded_files
from .workflow import execute_workflow

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "app" / "static"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
SESSIONS_DB = DATA_DIR / "sessions.db"

app = FastAPI(title="محرر — منظومة وكلاء مستقلة", version="2.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health")
async def health():
    return {"status": "ok", "agents_sdk": True}


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/manifest.webmanifest")
async def manifest():
    return FileResponse(STATIC_DIR / "manifest.webmanifest", media_type="application/manifest+json")


@app.get("/service-worker.js")
async def service_worker():
    return FileResponse(STATIC_DIR / "service-worker.js", media_type="application/javascript")


@app.post("/api/run")
async def run_document_workflow(
    x_openai_key: str = Header(..., alias="X-OpenAI-Key"),
    document_type: str = Form(...),
    user_request: str = Form(...),
    model: str = Form("gpt-5.4-mini"),
    files: list[UploadFile] = File(default=[]),
):
    key = x_openai_key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="مفتاح OpenAI مطلوب")
    if len(user_request.strip()) < 5:
        raise HTTPException(status_code=400, detail="الطلب قصير أو فارغ")

    try:
        source_text, manifest = await extract_uploaded_files(files)
        result = await execute_workflow(
            api_key=key,
            model=model.strip() or "gpt-5.4-mini",
            document_type=document_type.strip(),
            user_request=user_request.strip(),
            source_text=source_text,
            sessions_db=SESSIONS_DB,
        )
        result["files"] = manifest
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        # لا يُسجل المفتاح ولا يُعاد في الاستجابة.
        raise HTTPException(status_code=500, detail=f"فشل تشغيل منظومة الوكلاء: {exc}") from exc


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))

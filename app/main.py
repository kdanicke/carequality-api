from __future__ import annotations
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from .api.routes.meta import router as meta_router
from fastapi.middleware.cors import CORSMiddleware

from .db import engine, Base
from .api.routes.hospitals import router as hospitals_router, stats_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CareQuality API",
    version="0.1.0",
    description="Dataset-backed API for browsing CMS hospital/provider quality information (non-sensitive).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # If exc.detail already matches our error schema, return it.
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    # Otherwise wrap.
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "HTTP_ERROR", "message": str(exc.detail)}},
    )

app.include_router(hospitals_router)
app.include_router(stats_router)
app.include_router(meta_router)

@app.get("/health")
def health():
    return {"status": "ok"}
from fastapi import APIRouter, Depends, Response, UploadFile, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
from dependency_injector.wiring import inject, Provide
from typing import Annotated
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(prefix="/models", tags=["Models"])
templates = Jinja2Templates(directory="app/templates")

"""
    Requests de los endpoints
"""

@router.get("")
def models_get(request: Request):
    carpeta = Path("app/infrastructure/data/models")

    # Obtener solo archivos (excluye subdirectorios)
    MODEL_NAMES = [f.name for f in carpeta.iterdir() if f.is_file()]

    return templates.TemplateResponse("models.html", {"request": request, "modelos": MODEL_NAMES})

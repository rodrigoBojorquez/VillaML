from fastapi import APIRouter, Depends, Response, UploadFile, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dependency_injector.wiring import inject, Provide
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


router = APIRouter(prefix="/form", tags=["Form"])
templates = Jinja2Templates(directory="app/templates")

"""
    Requests de los endpoints
"""

@router.get("", response_class=HTMLResponse)
def mostrar_formulario(request: Request, archivo: str):
    return templates.TemplateResponse("form.html", {"request": request, "archivo": archivo})

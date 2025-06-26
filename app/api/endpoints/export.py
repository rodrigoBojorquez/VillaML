from fastapi import APIRouter, Depends, Response, UploadFile, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dependency_injector.wiring import inject, Provide
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


router = APIRouter(prefix="/export", tags=["Export"])
templates = Jinja2Templates(directory="app/templates")

"""
    Requests de los endpoints
"""


@router.get("", response_class=HTMLResponse)
@inject
async def get_export_view(request: Request):

    """
    Endpoint para obtener información de una sesión.
    """

    return templates.TemplateResponse("export.html", {"request": request})


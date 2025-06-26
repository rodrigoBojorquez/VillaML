from fastapi import APIRouter, Depends, Response, UploadFile, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dependency_injector.wiring import inject, Provide
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")

"""
    Requests de los endpoints
"""


@router.get("", response_class=HTMLResponse)
async def get_dashboard_view(request: Request, resultado: str = ""):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "resultado": resultado
    })


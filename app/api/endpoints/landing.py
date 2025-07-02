from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

router = APIRouter(prefix="", tags=["Landing"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def show_form(request: Request, success: Optional[bool] = False):
    return templates.TemplateResponse("landing.html", {
        "request": request,
        "success": success
    })



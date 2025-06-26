
from fastapi import APIRouter, Depends, Response, UploadFile, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from pathlib import Path
import joblib

router = APIRouter(prefix="/run", tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")

@router.post("")
async def run_model(
    request: Request,
    model_name: str = Form(...),
    age: float = Form(...),
    gender: int = Form(...),
    academic_level: int = Form(...),
    usage_hours: float = Form(...),
    platform: int = Form(...),
    academic_impact: int = Form(...),
    sleep_hours: float = Form(...),
    relationship: int = Form(...),
    conflicts: int = Form(...),
    addiction: int = Form(...)
):
    modelo_path = Path("app/infrastructure/data/models") / model_name

    try:
        modelo = joblib.load(modelo_path)
        input_data = [[
            age, gender, academic_level,
            usage_hours, platform, academic_impact,
            sleep_hours, relationship, conflicts, addiction
        ]]

        resultado = modelo.predict(input_data)[0]
        return RedirectResponse(f"/dashboard?resultado={resultado}", status_code=302)
    except Exception as e:
        return templates.TemplateResponse("form.html", {
            "request": request,
            "archivo": model_name,
            "error": str(e)
        })

    query_params = urlencode({"resultado": resultado})
    return RedirectResponse(url=f"/dashboard?{query_params}", status_code=302)

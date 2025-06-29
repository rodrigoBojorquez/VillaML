from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from pathlib import Path
import csv
import json

router = APIRouter(prefix="/form", tags=["Form"])
templates = Jinja2Templates(directory="app/templates")

"""
    Endpoints del formulario corto
"""

# GET → Muestra el formulario
@router.get("", response_class=HTMLResponse)
def mostrar_formulario(request: Request, success: Optional[bool] = False):
    return templates.TemplateResponse("form.html", {
        "request": request,
        "success": success
    })


# POST → Procesa el formulario
@router.post("")
async def procesar_formulario(
    request: Request,
    age: float = Form(...),
    academic_level: int = Form(...),
    usage_hours: float = Form(...),
    sleep_hours: float = Form(...),
    academic_impact: int = Form(...),
    conflict_level: int = Form(...)
):
    # Cargar datos anteriores si existen
    archivo_json = Path("app/infrastructure/data/respuestas.json")
    respuestas = []

    if archivo_json.exists():
        with archivo_json.open("r") as jf:
            try:
                respuestas = json.load(jf)
            except json.JSONDecodeError:
                respuestas = []

    # Asignar ID autoincremental
    nuevo_id = len(respuestas) + 1

    datos_con_id = {
        "id": nuevo_id,
        "edad": age,
        "nivel": academic_level,
        "uso_diario": usage_hours,
        "sueno": sleep_hours,
        "impacto": academic_impact,
        "conflictos": conflict_level
    }

    # Guardar en CSV
    archivo_csv = Path("app/infrastructure/data/respuestas.csv")
    archivo_csv.parent.mkdir(parents=True, exist_ok=True)
    existe_csv = archivo_csv.exists()

    with archivo_csv.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=datos_con_id.keys())
        if not existe_csv:
            writer.writeheader()
        writer.writerow(datos_con_id)

    # Guardar en JSON
    respuestas.append(datos_con_id)
    with archivo_json.open("w") as jf:
        json.dump(respuestas, jf, indent=2, ensure_ascii=False)

    # Redirección con éxito
    return RedirectResponse(url="/form?success=true", status_code=302)


# GET → Muestra las respuestas en JSON
@router.get("/respuestas", response_class=JSONResponse)
def ver_respuestas():
    archivo_json = Path("app/infrastructure/data/respuestas.json")

    if archivo_json.exists():
        try:
            with archivo_json.open("r") as f:
                datos = json.load(f)
            return JSONResponse(content=datos, status_code=200)
        except json.JSONDecodeError:
            return JSONResponse(content={"error": "El archivo JSON está dañado."}, status_code=500)
    else:
        return JSONResponse(content={"mensaje": "No hay datos disponibles."}, status_code=404)


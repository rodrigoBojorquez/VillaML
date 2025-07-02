from fastapi import APIRouter, Request, Form, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List
from pathlib import Path
import csv
import json

router = APIRouter(prefix="/form", tags=["Form"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def show_form(request: Request, success: Optional[bool] = False):
    return templates.TemplateResponse("form.html", {
        "request": request,
        "success": success
    })
    
@router.get("/landing", response_class=HTMLResponse)
def show_form(request: Request, success: Optional[bool] = False):
    return templates.TemplateResponse("landing.html", {
        "request": request,
        "success": success
    })



@router.post("")
async def process_form(
    request: Request,
    age: int = Form(...),
    academic_level: str = Form(...),
    gender: str = Form(...),
    country: str = Form(...),
    usage_hours: Optional[float] = Form(0.0),
    most_used_platform: str = Form(...),
    sleep_hours: Optional[float] = Form(0.0),
    academic_impact: int = Form(...),
    conflicts_over_social_media: int = Form(...),
    relationship_status: int = Form(...)
):
    json_file = Path("app/infrastructure/data/responses.json")
    responses = []

    # Crear archivo vacío si no existe
    if not json_file.exists():
        json_file.parent.mkdir(parents=True, exist_ok=True)  # Crear carpeta si no existe
        with json_file.open("w", encoding="utf-8") as jf:
            jf.write("[]")  # Escribir lista vacía

    # Leer respuestas previas
    try:
        with json_file.open("r", encoding="utf-8") as jf:
            responses = json.load(jf)
    except json.JSONDecodeError:
        responses = []

    # Leer respuestas previas para obtener el nuevo ID
    if json_file.exists():
        try:
            with json_file.open("r", encoding="utf-8") as jf:
                responses = json.load(jf)
        except json.JSONDecodeError:
            responses = []

    new_id = len(responses) + 1

    # Cálculo de Addicted_Score
    addicted_score = (
        (usage_hours * 10)
        + (10 if academic_impact == 1 else 0)
        + (10 if conflicts_over_social_media == 1 else 0)
        - (sleep_hours * 2)
    )

    if most_used_platform.lower() in ["tiktok", "instagram"]:
        addicted_score += 10
    elif most_used_platform.lower() == "snapchat":
        addicted_score += 5

    if relationship_status == 1:  # Suponiendo 1 = Single
        addicted_score += 5

    addicted_score = max(0, min(100, addicted_score))

    # Cálculo de Mental_Health_Score
    mental_health_score = (
        100
        - (addicted_score * 0.4)
        - (10 if academic_impact == 1 else 0)
        - (10 if conflicts_over_social_media == 1 else 0)
        + (sleep_hours * 2)
    )
    mental_health_score = max(0, min(100, mental_health_score))

    data_with_id = {
        "id": new_id,
        "age": age,
        "academic_level": academic_level,
        "gender": gender,
        "country": country,
        "daily_usage": usage_hours,
        "most_used_platform": most_used_platform,
        "sleep_hours": sleep_hours,
        "academic_impact": academic_impact,
        "conflicts": conflicts_over_social_media,
        "relationship_status": relationship_status,
        "addicted_score": round(addicted_score, 2),
        "mental_health_score": round(mental_health_score, 2),
    }

    csv_file = Path("app/infrastructure/data/responses.csv")
    csv_file.parent.mkdir(parents=True, exist_ok=True)
    csv_exists = csv_file.exists()

    with csv_file.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data_with_id.keys())
        if not csv_exists:
            writer.writeheader()
        writer.writerow(data_with_id)

    responses.append(data_with_id)
    with json_file.open("w", encoding="utf-8") as jf:
        json.dump(responses, jf, indent=2, ensure_ascii=False)

    return RedirectResponse(url="/form?success=true", status_code=302)

@router.get("/responses", response_class=JSONResponse)
def view_responses():
    json_file = Path("app/infrastructure/data/responses.json")

    if json_file.exists():
        try:
            with json_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return JSONResponse(content=data, status_code=200)
        except json.JSONDecodeError:
            return JSONResponse(content={"error": "The JSON file is corrupted."}, status_code=500)
    else:
        return JSONResponse(content={"message": "No data available."}, status_code=404)


@router.post("/bulk", response_class=JSONResponse)
async def bulk_register(data: List[dict] = Body(...)):
    """
    Espera un array JSON con objetos que tengan estas keys:
    - age (int)
    - academic_level (str)
    - gender (str)
    - country (str)
    - usage_hours (float)
    - most_used_platform (str)
    - sleep_hours (float)
    - academic_impact (int, 0/1)
    - conflicts_over_social_media (int, 0/1)
    - relationship_status (int, 0/1)
    """

    json_file = Path("app/infrastructure/data/responses.json")
    csv_file = Path("app/infrastructure/data/responses.csv")
    csv_file.parent.mkdir(parents=True, exist_ok=True)

    # Cargar respuestas previas o crear vacías
    responses = []
    if json_file.exists():
        try:
            with json_file.open("r", encoding="utf-8") as jf:
                responses = json.load(jf)
        except json.JSONDecodeError:
            responses = []

    # ID inicial basado en el tamaño actual
    current_id = len(responses)

    new_entries = []

    for entry in data:
        current_id += 1

        # Extraer campos con valores por defecto seguros
        usage_hours = float(entry.get("usage_hours", 0))
        academic_impact = int(entry.get("academic_impact", 0))
        conflicts = int(entry.get("conflicts_over_social_media", 0))
        sleep_hours = float(entry.get("sleep_hours", 0))
        relationship_status = int(entry.get("relationship_status", 0))
        most_used_platform = entry.get("most_used_platform", "").lower()

        # Cálculo de addicted_score
        addicted_score = (
            (usage_hours * 10)
            + (10 if academic_impact == 1 else 0)
            + (10 if conflicts == 1 else 0)
            - (sleep_hours * 2)
        )

        if most_used_platform in ["tiktok", "instagram"]:
            addicted_score += 10
        elif most_used_platform == "snapchat":
            addicted_score += 5

        if relationship_status == 1:
            addicted_score += 5

        addicted_score = max(0, min(100, addicted_score))

        # Cálculo de mental_health_score
        mental_health_score = (
            100
            - (addicted_score * 0.4)
            - (10 if academic_impact == 1 else 0)
            - (10 if conflicts == 1 else 0)
            + (sleep_hours * 2)
        )
        mental_health_score = max(0, min(100, mental_health_score))

        record = {
            "id": current_id,
            "age": int(entry.get("age", 0)),
            "academic_level": entry.get("academic_level", ""),
            "gender": entry.get("gender", ""),
            "country": entry.get("country", ""),
            "daily_usage": usage_hours,
            "most_used_platform": entry.get("most_used_platform", ""),
            "sleep_hours": sleep_hours,
            "academic_impact": academic_impact,
            "conflicts": conflicts,
            "relationship_status": relationship_status,
            "addicted_score": round(addicted_score, 2),
            "mental_health_score": round(mental_health_score, 2),
        }

        new_entries.append(record)
        responses.append(record)

    # Guardar en JSON
    with json_file.open("w", encoding="utf-8") as jf:
        json.dump(responses, jf, indent=2, ensure_ascii=False)

    # Guardar en CSV (modo append o crear encabezado si no existe)
    csv_exists = csv_file.exists()
    with csv_file.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=new_entries[0].keys())
        if not csv_exists:
            writer.writeheader()
        writer.writerows(new_entries)

    return JSONResponse(content={"message": f"{len(new_entries)} records added successfully."}, status_code=201)

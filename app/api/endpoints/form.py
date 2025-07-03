from fastapi import APIRouter, Request, Form, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List
from pathlib import Path
import csv
import json
import joblib
import pandas as pd
import numpy as np

router = APIRouter(prefix="/form", tags=["Form"])

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
            "Student_ID": current_id,
            "Age": int(entry.get("age", 0)),
            "Gender": entry.get("gender", ""),
            "Academic_Level": entry.get("academic_level", ""),
            "Country": entry.get("country", ""),
            "Avg_Daily_Usage_Hours": usage_hours,
            "Most_Used_Platform": entry.get("most_used_platform", ""),
            "Affects_Academic_Performance": academic_impact,
            "Sleep_Hours_Per_Night": sleep_hours,
            "Relationship_Status": relationship_status,
            "Conflicts_Over_Social_Media": conflicts,
            "addicted_score": round(addicted_score, 2),
            "mental_health_score": round(mental_health_score, 2)
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

@router.post("")
async def handle_form(
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
    # Binarizar género (male=1, else 0)
    gender_bin = 1 if gender.lower() == "male" else 0

    data = {
        "Age": age,
        "Avg_Daily_Usage_Hours": usage_hours,
        "Sleep_Hours_Per_Night": sleep_hours,
        "Conflicts_Over_Social_Media": conflicts_over_social_media,
        "Gender": gender_bin,
    }

    row = pd.DataFrame([data])

    model_addiction = joblib.load("app/infrastructure/data/models/model_addiction.pkl")
    model_mental = joblib.load("app/infrastructure/data/models/model_mental_health.pkl")

    addiction_pred = model_addiction.predict(row)[0]
    mental_pred = model_mental.predict(row)[0]

    # Limitar predicciones a rango [0, 100]
    addiction_pred = addiction_pred
    mental_pred = mental_pred

    addicted_score = (
        (usage_hours * 10)
        + (10 if academic_impact == 1 else 0)
        + (10 if conflicts_over_social_media == 1 else 0)
        - (sleep_hours * 2)
    )

    if most_used_platform.lower() in ["tiktok", "instagram"]:
        addicted_score += 10


    if relationship_status == 0:
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


    return RedirectResponse(
        status_code=200
    )

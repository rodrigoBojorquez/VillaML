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
import math

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
async def preview_processed_data(
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
    # Leer CSV original
    df = pd.read_csv("app/infrastructure/data/responses.csv")
    df = df.fillna(0)  # Evitar NaN en cálculos

    # Crear nuevo registro a partir de los datos recibidos
    new_row = {
        "Age": age,
        "Academic_Level": academic_level,
        "Gender": gender,
        "Country": country,
        "Avg_Daily_Usage_Hours": usage_hours,
        "Most_Used_Platform": most_used_platform,
        "Affects_Academic_Performance": academic_impact,
        "Sleep_Hours_Per_Night": sleep_hours,
        "Relationship_Status": relationship_status,
        "Conflicts_Over_Social_Media": conflicts_over_social_media,
    }

    # Agregar el nuevo registro al dataframe
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Eliminar columnas vacías o innecesarias
    df = df.drop(columns=['Unnamed: 11'], errors='ignore')

    # Función para calcular los scores de adicción y salud mental
    def calc_scores(row):
        usage = row.get('Avg_Daily_Usage_Hours', 0)
        academic = row.get('Affects_Academic_Performance', 0)
        conflicts = row.get('Conflicts_Over_Social_Media', 0)
        sleep = row.get('Sleep_Hours_Per_Night', 0)
        platform = str(row.get('Most_Used_Platform', '')).lower()
        relation = row.get('Relationship_Status', 0)

        addicted = (
            usage * 10
            + (10 if academic == 1 else 0)
            + (10 if conflicts == 1 else 0)
            - (sleep * 2)
        )
        if platform in ["tiktok", "instagram"]:
            addicted += 10
        elif platform == "snapchat":
            addicted += 5
        if relation == 1:
            addicted += 5
        addicted = max(0, min(100, addicted))

        mental = (
            100
            - addicted * 0.4
            - (10 if academic == 1 else 0)
            - (10 if conflicts == 1 else 0)
            + (sleep * 2)
        )
        mental = max(0, min(100, mental))

        return pd.Series([addicted, mental])

    # Aplicar la función a todas las filas
    df[['addicted_score', 'mental_health_score']] = df.apply(calc_scores, axis=1)

    # Factorizar columnas no numéricas para análisis posterior
    for col in df.columns:
        if not col.endswith('_num') and not pd.api.types.is_numeric_dtype(df[col]):
            df[f"{col}_num"] = pd.factorize(df[col])[0]

    # Obtener solo el último registro con sus scores
    latest = df.tail(1).iloc[0]

    user_addiction = latest['addicted_score']
    user_mental = latest['mental_health_score']

    recommendations = []

    # Generar recomendaciones basadas en scores
    if user_addiction >= 70:
        recommendations.append("⚠️ Alto nivel de adicción detectado. Considera reducir tu uso diario de redes sociales.")
    elif user_addiction >= 40:
        recommendations.append("📊 Nivel moderado de adicción. Puedes monitorear tu uso para evitar impactos negativos.")
    else:
        recommendations.append("✅ Tu nivel de adicción está dentro de un rango saludable.")

    if user_mental <= 40:
        recommendations.append("🧠 Tu salud mental podría estar viéndose afectada. Considera hábitos de autocuidado y descanso.")
    elif user_mental <= 60:
        recommendations.append("💡 Cuida tu descanso y emociones. Evitar conflictos digitales puede ayudar.")
    else:
        recommendations.append("🌟 Tu salud mental está en un buen estado. ¡Sigue cuidándola!")

    # Resultado a devolver
    result = latest.to_dict()
    result['recommendations'] = recommendations

    # Datos comparativos para gráficas
    comparison_data = {
        "addiction_distribution": df["addicted_score"].tolist(),
        "mental_health_distribution": df["mental_health_score"].tolist(),
        "user_scores": {
            "addicted_score": user_addiction,
            "mental_health_score": user_mental
        }
    }

    result["comparison_data"] = comparison_data

    def clean_dict(d):
        for k, v in d.items():
            if isinstance(v, float) and math.isnan(v):
                d[k] = None
            elif isinstance(v, dict):
                clean_dict(v)
            elif isinstance(v, list):
                for i in range(len(v)):
                    if isinstance(v[i], float) and math.isnan(v[i]):
                        v[i] = None
                    elif isinstance(v[i], dict):
                        clean_dict(v[i])

    clean_dict(result)

    return result
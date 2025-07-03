
from fastapi import APIRouter, Depends, Response, UploadFile, Request, Form
import pandas as pd

router = APIRouter(prefix="/data")

@router.get("/chart")
def get_chart_data():
    # Leer el CSV
    df = pd.read_csv('app/infrastructure/data/responses.csv')

    # Ejemplo de procesamiento de datos para cada gráfica:

    # 1) Distribución rendimiento académico vs adicción (suponiendo que tienes columna 'academic_performance' y 'addiction_level')
    academic_vs_addiction = df.groupby(['academic_performance', 'addiction_level']).size().reset_index(name='count')
    academic_vs_addiction_data = academic_vs_addiction.to_dict(orient='records')

    # 2) Clusters por edad en adicción (por ejemplo, agrupación simple)
    age_clusters = df.groupby('age')['addiction_level'].mean().reset_index()
    age_clusters_data = age_clusters.to_dict(orient='records')

    # 3) Predicción basada en edad (ejemplo simple)
    # Suponiendo que tienes predicciones ya guardadas en una columna 'predicted_addiction'
    if 'predicted_addiction' in df.columns:
        age_prediction = df[['age', 'predicted_addiction']].to_dict(orient='records')
    else:
        age_prediction = []

    # 4) Uso promedio de redes sociales base en adicción
    avg_use = df.groupby('addiction_level')['avg_daily_use_hours'].mean().reset_index()
    avg_use_data = avg_use.to_dict(orient='records')

    return {
        "academic_vs_addiction": academic_vs_addiction_data,
        "age_clusters": age_clusters_data,
        "age_prediction": age_prediction,
        "average_use": avg_use_data
    }

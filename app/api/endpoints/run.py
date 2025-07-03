
from fastapi import APIRouter, Depends, Response, UploadFile, Request, Form
from fastapi.templating import Jinja2Templates
from pandas import factorize
from pydantic import BaseModel
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.kernel_ridge import KernelRidge
from sklearn.ensemble import RandomForestRegressor


router = APIRouter(prefix="/run")
templates = Jinja2Templates(directory="app/templates")


# Modelo de datos para /predict
class PredictInput(BaseModel):
    Age: int
    Gender_num: int
    Academic_Level_num: int
    Country_num: int
    Avg_Daily_Usage_Hours: float
    Most_Used_Platform_num: int
    Affects_Academic_Performance_num: int
    Sleep_Hours_Per_Night: float
    Relationship_Status_num: int
    Conflicts_Over_Social_Media: int


@router.post("/process")
def process_data():
    df = pd.read_csv('app/infrastructure/data/responses.csv')

    def calc_scores(row):
        usage_hours = row['Avg_Daily_Usage_Hours']
        academic_impact = row['Affects_Academic_Performance']
        conflicts = row['Conflicts_Over_Social_Media']
        sleep_hours = row['Sleep_Hours_Per_Night']
        platform = str(row['Most_Used_Platform']).lower()
        relationship_status = row['Relationship_Status']

        addicted = (
            usage_hours * 10
            + (10 if academic_impact == 1 else 0)
            + (10 if conflicts == 1 else 0)
            - (sleep_hours * 2)
        )
        if platform in ["tiktok", "instagram"]:
            addicted += 10
        elif platform == "snapchat":
            addicted += 5
        if relationship_status == 1:
            addicted += 5
        addicted = max(0, min(100, addicted))

        mental = (
            100
            - addicted * 0.4
            - (10 if academic_impact == 1 else 0)
            - (10 if conflicts == 1 else 0)
            + (sleep_hours * 2)
        )
        mental = max(0, min(100, mental))

        return pd.Series([addicted, mental])

    df[['addicted_score', 'mental_health_score']] = df.apply(calc_scores, axis=1)

    # Convertir columnas no numéricas en columnas numéricas _num
    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            df[f"{col}_num"] = pd.factorize(df[col])[0]

    # Guardar cambios sobrescribiendo el archivo
    df.to_csv('app/infrastructure/data/responses.csv', index=False)

    return {"message": "Archivo modificado y guardado con nuevas columnas y versiones numéricas."}


@router.post("/train")
def train_models():
    df = pd.read_csv('app/infrastructure/data/responses.csv')

    features = [
        'Age',
        'Avg_Daily_Usage_Hours',
        'Sleep_Hours_Per_Night',
        'Conflicts_Over_Social_Media',
        'Gender_num',
        'Academic_Level_num',
        'Country_num',
        'Most_Used_Platform_num',
        'Affects_Academic_Performance_num',
        'Relationship_Status_num'
    ]

    X = df[features]

    y_addiction = df['addicted_score']
    y_mental = df['mental_health_score']

    # División para ambos objetivos con el mismo split
    X_train, X_test, y_train_add, y_test_add, y_train_mh, y_test_mh = train_test_split(
        X, y_addiction, y_mental, test_size=0.3, random_state=42
    )

    model_addiction = RandomForestRegressor(n_estimators=100, random_state=42)
    model_addiction.fit(X_train, y_train_add)

    model_mental = RandomForestRegressor(n_estimators=100, random_state=42)
    model_mental.fit(X_train, y_train_mh)

    joblib.dump(model_addiction, "app/infrastructure/data/models/model_addiction.pkl")
    joblib.dump(model_mental, "app/infrastructure/data/models/model_mental_health.pkl")

    return {
        "message": "Modelos de regresión entrenados y guardados correctamente",
        "features_usadas": features
    }

@router.post("/predict")
def predict(data: PredictInput):
    # Cargar modelos
    model_add = joblib.load("app/infrastructure/data/models/model_addiction.pkl")
    model_mh = joblib.load("app/infrastructure/data/models/model_mental_health.pkl")

    # Convertir input a DataFrame
    input_df = pd.DataFrame([data.dict()])

    # Predecir
    pred_add = model_add.predict(input_df)[0]
    pred_mh = model_mh.predict(input_df)[0]

    return {
        "Addiction_prediction": pred_add,
        "Mental_Health_prediction": pred_mh
    }

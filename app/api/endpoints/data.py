
from fastapi import APIRouter, Depends, Response, UploadFile, Request, Form, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import joblib

router = APIRouter(prefix="/data")

@router.get("/chart")
def get_chart_data():
    df = pd.read_csv('app/infrastructure/data/responses.csv')

    # 1. Academic vs Addiction
    academic_vs_addiction_data = df.groupby("Academic_Level")["addicted_score"].mean().reset_index()

    # 2. Age Clusters (agrupación por edad)
    age_kmeans = KMeans(n_clusters=3, random_state=0)
    df['age_cluster'] = pd.cut(df['Age'], bins=[10, 18, 25, 100], labels=[0, 1, 2])
    age_clusters_data = df.groupby("age_cluster")["addicted_score"].mean().reset_index()

    # 3. Age Prediction (regresión lineal)
    X = df[["Age"]]
    y = df["addicted_score"]
    model = LinearRegression().fit(X, y)
    age_range = pd.DataFrame({"Age": range(int(df["Age"].min()), int(df["Age"].max()) + 1)})
    age_range["Predicted_Addiction"] = model.predict(age_range[["Age"]])

    # 4. Average Use vs Addiction
    avg_use_data = df.groupby("Avg_Daily_Usage_Hours")["addicted_score"].mean().reset_index()

    # 5. Average Use per Age Cluster
    avg_use_age_cluster = df.groupby("age_cluster")["Avg_Daily_Usage_Hours"].mean().reset_index()
    
    # 6. Average Use per Age by Gender
    avg_use_age_gender = df.groupby(["Age", "Gender"])["Avg_Daily_Usage_Hours"].mean().reset_index()
    
    # 7. Average addiction per Age by Gender
    avg_addiction_age_gender = df.groupby(["Age", "Gender"])["addicted_score"].mean().reset_index()
    
    # 8. Average addiction by Sleep hours
    df["Sleep_Hours_Per_Night"] = df["Sleep_Hours_Per_Night"].astype(float).round()
    avg_addiction_sleep = df.groupby("Sleep_Hours_Per_Night")["addicted_score"].mean().reset_index().sort_values("Sleep_Hours_Per_Night")
    
    # 9. Average mental health by Age
    avg_mh_age = df.groupby("Age")["mental_health_score"].mean().reset_index().sort_values("Age")
    
    # 10. Average mental health by use
    df["Avg_Daily_Usage_Hours"] = df["Avg_Daily_Usage_Hours"].astype(float).round()
    avg_mh_use = df.groupby("Avg_Daily_Usage_Hours")["mental_health_score"].mean().reset_index().sort_values("Avg_Daily_Usage_Hours")

    return {
        "academic_vs_addiction": academic_vs_addiction_data.to_dict(orient="records"),
        "age_clusters": age_clusters_data.to_dict(orient="records"),
        "age_prediction": age_range.to_dict(orient="records"),
        "average_use": avg_use_data.to_dict(orient="records"),
        "average_use_age_cluster": avg_use_age_cluster.to_dict(orient="records"),
        "average_use_age_gender": avg_use_age_gender.to_dict(orient="records"),
        "average_addiction_age_gender": avg_addiction_age_gender.to_dict(orient="records"),
        "average_addiction_sleep": avg_addiction_sleep.to_dict(orient="records"),
        "average_mh_age": avg_mh_age.to_dict(orient="records"),
        "average_mh_use": avg_mh_use.to_dict(orient="records"),
    }
    



@router.post("/academic_vs_addiction")
async def receive_personal_data(data: Dict[str, Any] = Body(...)):
    df = pd.read_csv('app/infrastructure/data/responses.csv')

    user_academic_level = data.get("Academic_Level")
    user_age = data.get("Age")
    user_addiction_score = data.get("addicted_score")

    academic_vs_addiction_data = df.groupby("Academic_Level")["addicted_score"].mean().reset_index()

    user_level_avg = academic_vs_addiction_data.loc[
        academic_vs_addiction_data["Academic_Level"] == user_academic_level,
        "addicted_score"
    ]

    avg_for_user_level = float(user_level_avg.iloc[0]) if not user_level_avg.empty else None

    if avg_for_user_level is not None:
        tolerance = avg_for_user_level * 0.05
        lower_bound = avg_for_user_level - tolerance
        upper_bound = avg_for_user_level + tolerance

        if user_addiction_score > upper_bound:
            comparison_result = "above average"
            description = "Estas por encima del promedio de adicción para tu nivel académico, un cambio de hábitos vendría bien."
        elif user_addiction_score < lower_bound:
            comparison_result = "below average"
            description = "Felicidades! Estás debajo del promedio de adicción para tu nivel académico, sigue así."
        else:
            comparison_result = "around average"
            description = "Tu nivel de adicción está dentro del rango para tu nivel académico. Aun así, mantener hábitos saludables es importante."
    else:
        comparison_result = "unknown (academic level not in dataset)"
        description = "No se encontró tu nivel académico en la base de datos para comparar."

    return JSONResponse(content={
        "academic_vs_addiction": {        
        "user_addicted_score": user_addiction_score,
        "user_academic_level": user_academic_level,
        "average_for_same_level": avg_for_user_level,
        "comparison_result": comparison_result,
        "description": description },
    })
    
@router.post("/age_clusters")
async def receive_personal_data(data: Dict[str, Any] = Body(...)):
    df = pd.read_csv('app/infrastructure/data/responses.csv')

    df['age_cluster'] = pd.cut(df['Age'], bins=[10, 18, 25, 100], labels=[0, 1, 2])
    age_clusters_data = df.groupby("age_cluster")["addicted_score"].mean().reset_index()

    user_age = data.get("Age")
    user_score = data.get("addicted_score")

    # Determinar en qué cluster cae su edad
    user_cluster = pd.cut([user_age], bins=[10, 18, 25, 100], labels=[0, 1, 2])[0]

    # Obtener promedio de ese cluster
    cluster_avg_row = age_clusters_data.loc[age_clusters_data["age_cluster"] == user_cluster, "addicted_score"]
    cluster_avg = float(cluster_avg_row.iloc[0]) if not cluster_avg_row.empty else None

    if cluster_avg is not None:
        tolerance = cluster_avg * 0.05
        lower = cluster_avg - tolerance
        upper = cluster_avg + tolerance

        if user_score > upper:
            comparison = "La adiccion se encuentra por encima del promedio para el rango de edad. deberia considerar un cambio de habitos"
        elif user_score < lower:
            comparison = "Felicidades! Estás debajo del promedio de adicción dentro de tu rango de edad, sigue así."
        else:
            comparison = "Tu nivel de adicción está dentro del rango para rango de edad. Aun así, mantener hábitos saludables es importante."
    else:
        comparison = "unknown (age out of range)"

    return JSONResponse(content={
        "user_age": user_age,
        "user_score": user_score,
        "user_cluster": str(user_cluster),
        "cluster_average_score": cluster_avg,
        "comparison": comparison
    })
    
        
@router.post("/age_prediction")
async def receive_personal_data(data: Dict[str, Any] = Body(...)):
    model_path = "app/infrastructure/data/models/model_Age_based_on_add.pkl"
    
    user_score = data.get("addicted_score")
    if user_score is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing 'addicted_score' in request body"}
        )
    try:
        # Load the model
        model = joblib.load(model_path)

        # Predict age
        predicted_age = float(model.predict([[user_score]])[0])

        return JSONResponse(content={
            "user_addicted_score": user_score,
            "predicted_age": round(predicted_age, 2),
            "note": f"Basado en tu nivel de adicción, nuestro modelo predice que tu edad es de {round(predicted_age, 2)} años."
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Prediction failed: {str(e)}"}
        )

@router.post("/average_age")
async def receive_personal_data(data: Dict[str, Any] = Body(...)):
    model_path = "app/infrastructure/data/models/model_Age_based_on_add.pkl"
    
    user_score = data.get("addicted_score")
    if user_score is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing 'addicted_score' in request body"}
        )
    try:
        model = joblib.load(model_path)
        predicted_age = float(model.predict([[user_score]])[0])

        return JSONResponse(content={
            "user_addicted_score": user_score,
            "predicted_age": round(predicted_age, 2),
            "note": f"Basado en tu nivel de adicción, nuestro modelo predice que tu edad es de {round(predicted_age, 2)} años."
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Prediction failed: {str(e)}"}
        )
        
@router.post("/average_use_on_add")
async def receive_personal_data(data: Dict[str, Any] = Body(...)):
    model_path = "app/infrastructure/data/models/model_Use_based_on_add.pkl"
    
    user_score = data.get("addicted_score")
    if user_score is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing 'addicted_score' in request body"}
        )
    try:
        model = joblib.load(model_path)
        predicted_use = float(model.predict([[user_score]])[0])

        return JSONResponse(content={
            "user_addicted_score": user_score,
            "predicted_use": round(predicted_use, 2),
            "note": f"Basado en tu nivel de adicción, nuestro modelo predice que usas {round(predicted_use, 2)}h al dia."
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Prediction failed: {str(e)}"}
        )
        
@router.post("/usage_by_age_cluster")
async def compare_usage_by_age_cluster(data: Dict[str, Any] = Body(...)):
    df = pd.read_csv('app/infrastructure/data/responses.csv')
    
    df['age_cluster'] = pd.cut(df['Age'], bins=[10, 18, 25, 100], labels=[0, 1, 2])
    usage_by_cluster = df.groupby("age_cluster")["Avg_Daily_Usage_Hours"].mean().reset_index()

    user_age = data.get("Age")
    user_usage = data.get("Avg_Daily_Usage_Hours")
    user_cluster = pd.cut([user_age], bins=[10, 18, 25, 100], labels=[0, 1, 2])[0]

    cluster_avg_row = usage_by_cluster.loc[usage_by_cluster["age_cluster"] == user_cluster, "Avg_Daily_Usage_Hours"]
    cluster_avg = float(cluster_avg_row.iloc[0]) if not cluster_avg_row.empty else None

    if cluster_avg is not None:
        tolerance = cluster_avg * 0.05
        lower = cluster_avg - tolerance
        upper = cluster_avg + tolerance

        if user_usage > upper:
            comparison = "Tu tiempo de uso diario está por encima del promedio para tu grupo de edad. Considera reducir tu tiempo en redes."
        elif user_usage < lower:
            comparison = "Estás por debajo del promedio de uso diario para tu grupo de edad. ¡Buen trabajo!"
        else:
            comparison = "Tu tiempo de uso está dentro del rango promedio para tu grupo de edad."
    else:
        comparison = "unknown (age out of range)"

    return JSONResponse(content={
        "user_age": user_age,
        "user_usage_hours": user_usage,
        "user_cluster": str(user_cluster),
        "cluster_average_usage": cluster_avg,
        "comparison": comparison
    })

@router.post("/usage_by_age_gender")
async def compare_usage_by_age_and_gender(data: Dict[str, Any] = Body(...)):
    df = pd.read_csv('app/infrastructure/data/responses.csv')

    # Agrupar por Edad + Género
    avg_use_age_gender = df.groupby(["Age", "Gender"])["Avg_Daily_Usage_Hours"].mean().reset_index()

    # Datos del usuario
    user_age = data.get("Age")
    user_gender = data.get("Gender")
    user_usage = data.get("Avg_Daily_Usage_Hours")

    # Buscar el promedio para esa combinación
    match_row = avg_use_age_gender.loc[
        (avg_use_age_gender["Age"] == user_age) & 
        (avg_use_age_gender["Gender"] == user_gender),
        "Avg_Daily_Usage_Hours"
    ]

    gender_age_avg = float(match_row.iloc[0]) if not match_row.empty else None

    # Comparación con 5% de tolerancia
    if gender_age_avg is not None:
        tolerance = gender_age_avg * 0.05
        lower = gender_age_avg - tolerance
        upper = gender_age_avg + tolerance

        if user_usage > upper:
            comparison = "Estás usando redes más tiempo de lo habitual para personas de tu edad y género."
        elif user_usage < lower:
            comparison = "Estás por debajo del promedio de uso en tu grupo de edad y género. ¡Bien hecho!"
        else:
            comparison = "Tu uso está dentro del promedio de tu edad y género."
    else:
        comparison = "No se encontró promedio para tu edad y género."

    return JSONResponse(content={
        "user_age": user_age,
        "user_gender": user_gender,
        "user_usage_hours": user_usage,
        "gender_age_average_usage": gender_age_avg,
        "comparison": comparison
    })

@router.post("/addiction_by_age_gender")
async def compare_addiction_by_age_and_gender(data: Dict[str, Any] = Body(...)):
    df = pd.read_csv('app/infrastructure/data/responses.csv')

    avg_addiction_age_gender = df.groupby(["Age", "Gender"])["addicted_score"].mean().reset_index()

    user_age = data.get("Age")
    user_gender = data.get("Gender")
    user_addicted_score = data.get("addicted_score")

    match_row = avg_addiction_age_gender.loc[
        (avg_addiction_age_gender["Age"] == user_age) &
        (avg_addiction_age_gender["Gender"] == user_gender),
        "addicted_score"
    ]

    group_avg = float(match_row.iloc[0]) if not match_row.empty else None

    if group_avg is not None:
        tolerance = group_avg * 0.05
        lower = group_avg - tolerance
        upper = group_avg + tolerance

        if user_addicted_score > upper:
            comparison = "Tu nivel de adicción está por encima del promedio para tu edad y género."
        elif user_addicted_score < lower:
            comparison = "Tu nivel de adicción está por debajo del promedio para tu edad y género. ¡Bien hecho!"
        else:
            comparison = "Tu nivel de adicción está dentro del promedio para tu grupo."
    else:
        comparison = "No se encontró promedio para tu grupo de edad y género."

    return JSONResponse(content={
        "user_age": user_age,
        "user_gender": user_gender,
        "user_addicted_score": user_addicted_score,
        "group_average_addicted_score": group_avg,
        "comparison": comparison
    })

@router.post("/average_add_on_sleep")
async def receive_personal_data(data: Dict[str, Any] = Body(...)):
    model_path = "app/infrastructure/data/models/model_Add_based_on_sleep.pkl"
    
    user_sleep = data.get("Sleep_Hours_Per_Night")
    if user_sleep is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing 'Sleep_Hours_Per_Night' in request body"}
        )
    try:
        model = joblib.load(model_path)
        predicted_use = float(model.predict([[user_sleep]])[0])

        return JSONResponse(content={
            "user_sleep_hours": user_sleep,
            "predicted_add": round(predicted_use, 2),
            "note": f"Basado en tu nivel de sueño, nuestro modelo predice que tu adiccion deberia ser de {round(predicted_use, 2)} puntos."
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Prediction failed: {str(e)}"}
        )
        
@router.post("/average_mh_by_age")
async def receive_personal_data(data: Dict[str, Any] = Body(...)):
    model_path = "app/infrastructure/data/models/model_mh_based_on_age.pkl"
    
    user_Age = data.get("Age")
    if user_Age is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing 'Age' in request body"}
        )
    try:
        model = joblib.load(model_path)
        predicted_use = float(model.predict([[user_Age]])[0])

        return JSONResponse(content={
            "user_Age": user_Age,
            "predicted_mh": round(predicted_use, 2),
            "note": f"Basado en tu edad, nuestro modelo predice que tu salud mental deberia de ser de {round(predicted_use, 2)} puntos."
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Prediction failed: {str(e)}"}
        )
        
@router.post("/average_mh_by_use")
async def receive_personal_data(data: Dict[str, Any] = Body(...)):
    model_path = "app/infrastructure/data/models/model_mh_based_on_use.pkl"
    
    user_var = data.get("Avg_Daily_Usage_Hours")
    if user_var is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing 'Avg_Daily_Usage_Hours' in request body"}
        )
    try:
        model = joblib.load(model_path)
        predicted_use = float(model.predict([[user_var]])[0])

        return JSONResponse(content={
            "user_use_hours": user_var,
            "predicted_mh": round(predicted_use, 2),
            "note": f"Basado en tu tiempo en pantalla, nuestro modelo predice que tu salud mental deberia de ser de {round(predicted_use, 2)} puntos."
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Prediction failed: {str(e)}"}
        )
        
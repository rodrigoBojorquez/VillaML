
from fastapi import APIRouter, Depends, Response, UploadFile, Request, Form
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

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

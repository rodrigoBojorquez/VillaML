import joblib
from config.settings import Settings

MODELS = {}

def load_models():
    names = [
      "dailyUseVsAddiction_cluster",
      "dailyHoursVsMentalHealth_decision_tree",
      "dailyVsAcademicPerformance_kernel",
      "diarioVsSalud_regression_lineal",
      "sleepVsMentalHealth_isotonic",
    ]
    for n in names:
        path = f"{Settings.MODEL_DIR}/{n}.pkl"
        MODELS[n] = joblib.load(path)
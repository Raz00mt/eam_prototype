# from datetime import datetime, timedelta

# def baseline_rul_days(temperature: float, vibration: float, operating_hours: float) -> int:
#     """
#     Заглушка на MVP:
#     чем хуже параметры, тем меньше RUL.
#     Потом заменим на sklearn-модель, не меняя UI.
#     """
#     # базовый ресурс
#     rul = 180

#     # штрафы
#     rul -= int(max(0, (temperature - 40) * 2))     # перегрев
#     rul -= int(max(0, (vibration - 0.3) * 120))    # вибрация
#     rul -= int(max(0, (operating_hours - 3000) / 50))  # наработка

#     # ограничим
#     return max(7, min(365, rul))

# def predict_failure_date(rul_days: int) -> datetime:
#     return datetime.now() + timedelta(days=int(rul_days))

# from datetime import datetime, timedelta
# from pathlib import Path
# import joblib

# from src.services.health_index import calculate_its

# MODEL_PATH = Path("src/ml/artifacts/rul_model.joblib")


# def load_model():
#     if not MODEL_PATH.exists():
#         return None
#     return joblib.load(MODEL_PATH)


# def predict_rul_days(temperature: float, vibration: float, operating_hours: float) -> int:
#     model = load_model()

#     # fallback, если модель ещё не обучена
#     if model is None:
#         return baseline_rul_days(temperature, vibration, operating_hours)

#     health_index, _ = calculate_its(temperature, vibration, operating_hours)

#     X = [[temperature, vibration, operating_hours, health_index]]
#     pred = model.predict(X)[0]

#     pred = int(round(pred))
#     return max(7, min(365, pred))


# def baseline_rul_days(temperature: float, vibration: float, operating_hours: float) -> int:
#     rul = 180
#     rul -= int(max(0, (temperature - 40) * 2))
#     rul -= int(max(0, (vibration - 0.3) * 120))
#     rul -= int(max(0, (operating_hours - 3000) / 50))
#     return max(7, min(365, rul))


# def predict_failure_date(rul_days: int) -> datetime:
#     return datetime.now() + timedelta(days=int(rul_days))

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import joblib

from src.services.health_index import calculate_its

MODEL_PATH = Path("src/ml/artifacts/rul_model.joblib")


def load_model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


def predict_rul_days(temperature: float, vibration: float, operating_hours: float) -> int:
    model = load_model()

    if model is None:
        return baseline_rul_days(temperature, vibration, operating_hours)

    health_index, _ = calculate_its(temperature, vibration, operating_hours)

    X = pd.DataFrame([{
        "temperature": temperature,
        "vibration": vibration,
        "operating_hours": operating_hours,
        "health_index": health_index,
    }])

    pred = model.predict(X)[0]
    pred = int(round(pred))
    return max(7, min(365, pred))


def baseline_rul_days(temperature: float, vibration: float, operating_hours: float) -> int:
    rul = 180
    rul -= int(max(0, (temperature - 40) * 2))
    rul -= int(max(0, (vibration - 0.3) * 120))
    rul -= int(max(0, (operating_hours - 3000) / 50))
    return max(7, min(365, rul))


def predict_failure_date(rul_days: int) -> datetime:
    return datetime.now() + timedelta(days=int(rul_days))
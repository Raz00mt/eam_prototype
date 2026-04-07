from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sqlalchemy import text

from src.db.session import engine

ARTIFACTS_DIR = Path("src/ml/artifacts")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def load_training_data():
    query = """
    SELECT
        temperature,
        vibration,
        operating_hours,
        health_index,
        rul_days
    FROM equipment_ml_samples
    """
    return pd.read_sql(text(query), engine)


def train_model():
    df = load_training_data()

    X = df[["temperature", "vibration", "operating_hours", "health_index"]]
    y = df["rul_days"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        random_state=42
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    metrics = {
        "mae": float(mean_absolute_error(y_test, preds)),
        "r2": float(r2_score(y_test, preds)),
    }

    joblib.dump(model, ARTIFACTS_DIR / "rul_model.joblib")
    joblib.dump(metrics, ARTIFACTS_DIR / "metrics.joblib")

    print("Модель обучена")
    print(metrics)


if __name__ == "__main__":
    train_model()
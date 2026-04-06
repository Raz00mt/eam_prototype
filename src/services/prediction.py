from datetime import datetime, timedelta

def baseline_rul_days(temperature: float, vibration: float, operating_hours: float) -> int:
    """
    Заглушка на MVP:
    чем хуже параметры, тем меньше RUL.
    Потом заменим на sklearn-модель, не меняя UI.
    """
    # базовый ресурс
    rul = 180

    # штрафы
    rul -= int(max(0, (temperature - 40) * 2))     # перегрев
    rul -= int(max(0, (vibration - 0.3) * 120))    # вибрация
    rul -= int(max(0, (operating_hours - 3000) / 50))  # наработка

    # ограничим
    return max(7, min(365, rul))

def predict_failure_date(rul_days: int) -> datetime:
    return datetime.now() + timedelta(days=int(rul_days))
import numpy as np
import pandas as pd
from datetime import date, timedelta

def calculate_its(temp: float, vibration: float, hours: float):
    """
    Возвращает:
      its (0..1)
      parts: нормированные подоценки
    """
    # Параметры (можно вынести в БД/справочник)
    temp_norm = 20.0
    temp_crit = 80.0
    vib_crit = 1.0
    hours_max = 10000.0

    # Нормировка 0..1 (1 хорошо, 0 плохо)
    s_temp = 1 - (temp - temp_norm) / (temp_crit - temp_norm)
    s_vib = 1 - (vibration / vib_crit)
    s_hours = 1 - (hours / hours_max)

    s_temp = float(np.clip(s_temp, 0, 1))
    s_vib = float(np.clip(s_vib, 0, 1))
    s_hours = float(np.clip(s_hours, 0, 1))

    # Веса
    its = 0.4 * s_temp + 0.4 * s_vib + 0.2 * s_hours
    its = float(np.clip(its, 0, 1))

    return its, {"s_temp": s_temp, "s_vib": s_vib, "s_hours": s_hours}

def its_status(its_percent: float) -> str:
    if its_percent >= 80:
        return "Исправно"
    if its_percent >= 60:
        return "Допустимо"
    if its_percent >= 40:
        return "Ухудшение"
    return "Критично"

def its_forecast_curve_variant_b(
    its0: float,
    its_crit: float,
    rul_days: int,
    p: float = 2.0,
):
    rul_days = int(max(1, rul_days))
    p = float(max(0.5, p))

    t = np.arange(0, rul_days + 1)
    x = 1 - (t / rul_days)  # 1..0
    its = its_crit + (its0 - its_crit) * (x ** p)
    its = np.clip(its, 0, 1)

    start = date.today()
    dates = [start + timedelta(days=int(i)) for i in t]

    return pd.DataFrame({"date": dates, "its": its, "its_percent": its * 100})

def its_status_color(its_percent: float) -> str:
    if its_percent >= 80:
        return "#16a34a"   # зелёный
    if its_percent >= 60:
        return "#eab308"   # жёлтый
    if its_percent >= 40:
        return "#f97316"   # оранжевый
    return "#dc2626"       # красный
from datetime import datetime, timedelta
import random

from sqlalchemy.orm import Session

from src.db.models import Base, Equipment, EquipmentMLSample
from src.db.session import engine
from src.services.health_index import calculate_its
from src.db import crud


def init_db():
    Base.metadata.create_all(bind=engine)


def seed_demo(db: Session):
    if crud.list_equipment(db):
        return

    equipment_list = [
        Equipment(equipment_name="Генератор АБ4", equipment_type="Генератор", location="Цех 1", status="Работает"),
        Equipment(equipment_name="Насос N12", equipment_type="Насос", location="Цех 2", status="Работает"),
        Equipment(equipment_name="Компрессор K7", equipment_type="Компрессор", location="Цех 3", status="Работает"),
        Equipment(equipment_name="Вентилятор V5", equipment_type="Вентилятор", location="Цех 4", status="Работает"),
        Equipment(equipment_name="Редуктор R3", equipment_type="Редуктор", location="Цех 5", status="Работает"),
    ]
    db.add_all(equipment_list)
    db.commit()

    for eq in equipment_list:
        seed_equipment_history(db, eq)


def seed_equipment_history(db: Session, equipment: Equipment):
    start_date = datetime.now() - timedelta(days=180)

    # Профили оборудования
    if equipment.equipment_name == "Вентилятор V5":
        # Хорошее состояние: ИТС около 75-80
        base_temp = 30
        base_vibration = 0.18
        base_hours = 1800
        temp_growth = 0.01
        vib_growth = 0.001
        hour_growth = 10

    elif equipment.equipment_name == "Редуктор R3":
        # Хорошее/допустимое состояние: ИТС около 70-75
        base_temp = 34
        base_vibration = 0.25
        base_hours = 2600
        temp_growth = 0.015
        vib_growth = 0.0015
        hour_growth = 11

    elif equipment.equipment_name == "Генератор АБ4":
        # Среднее состояние
        base_temp = 38
        base_vibration = 0.28
        base_hours = 3200
        temp_growth = 0.025
        vib_growth = 0.002
        hour_growth = 12

    elif equipment.equipment_name == "Насос N12":
        # Более деградировавшее
        base_temp = 45
        base_vibration = 0.42
        base_hours = 5200
        temp_growth = 0.035
        vib_growth = 0.003
        hour_growth = 13

    else:
        # Компрессор K7 — ухудшенное состояние
        base_temp = 50
        base_vibration = 0.55
        base_hours = 6500
        temp_growth = 0.04
        vib_growth = 0.0035
        hour_growth = 14

    for day in range(180):
        ts = start_date + timedelta(days=day)

        temperature = base_temp + day * temp_growth + random.uniform(-0.8, 0.8)
        vibration = base_vibration + day * vib_growth + random.uniform(-0.015, 0.015)
        operating_hours = base_hours + day * hour_growth

        temperature = round(max(20, temperature), 2)
        vibration = round(max(0.05, vibration), 3)
        operating_hours = round(operating_hours, 1)

        its, parts = calculate_its(temperature, vibration, operating_hours)

        rul_days = max(7, int(its * 180) + random.randint(-5, 5))

        crud.add_measurement_with_ts(
            db=db,
            equipment_id=equipment.equipment_id,
            ts=ts,
            temperature=temperature,
            vibration=vibration,
            operating_hours=operating_hours,
            pressure=None,
        )

        crud.save_health_index_with_ts(
            db=db,
            equipment_id=equipment.equipment_id,
            ts=ts,
            health_index=its,
            temperature_score=parts["s_temp"],
            vibration_score=parts["s_vib"],
            hours_score=parts["s_hours"],
        )

        sample = EquipmentMLSample(
            equipment_id=equipment.equipment_id,
            ts=ts,
            temperature=temperature,
            vibration=vibration,
            operating_hours=operating_hours,
            pressure=None,
            health_index=its,
            rul_days=rul_days,
        )
        db.add(sample)

    db.commit()


def bootstrap():
    init_db()
    from src.db.session import get_session
    db = get_session()
    try:
        seed_demo(db)
    finally:
        db.close()


if __name__ == "__main__":
    bootstrap()
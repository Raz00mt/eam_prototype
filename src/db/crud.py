from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from src.db.models import Equipment, EquipmentMeasurement, EquipmentHealthIndex, EquipmentPrediction

def list_equipment(db: Session):
    return db.execute(select(Equipment).order_by(Equipment.equipment_name)).scalars().all()

def get_equipment(db: Session, equipment_id: int):
    return db.get(Equipment, equipment_id)

def get_latest_measurement(db: Session, equipment_id: int):
    stmt = (
        select(EquipmentMeasurement)
        .where(EquipmentMeasurement.equipment_id == equipment_id)
        .order_by(desc(EquipmentMeasurement.ts))
        .limit(1)
    )
    return db.execute(stmt).scalars().first()

def add_measurement(
    db: Session,
    equipment_id: int,
    temperature: float,
    vibration: float,
    operating_hours: float,
    pressure: float | None = None,
):
    m = EquipmentMeasurement(
        equipment_id=equipment_id,
        temperature=temperature,
        vibration=vibration,
        operating_hours=operating_hours,
        pressure=pressure,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

def save_health_index(
    db: Session,
    equipment_id: int,
    health_index: float,
    temperature_score: float,
    vibration_score: float,
    hours_score: float,
):
    h = EquipmentHealthIndex(
        equipment_id=equipment_id,
        health_index=health_index,
        temperature_score=temperature_score,
        vibration_score=vibration_score,
        hours_score=hours_score,
    )
    db.add(h)
    db.commit()
    db.refresh(h)
    return h

def save_prediction(
    db: Session,
    equipment_id: int,
    rul_days: int,
    predicted_failure_date,
    failure_probability: float | None,
    model_version: str = "baseline-v1",
):
    p = EquipmentPrediction(
        equipment_id=equipment_id,
        rul_days=rul_days,
        predicted_failure_date=predicted_failure_date,
        failure_probability=failure_probability,
        model_version=model_version,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

def get_latest_health(db: Session, equipment_id: int):
    stmt = (
        select(EquipmentHealthIndex)
        .where(EquipmentHealthIndex.equipment_id == equipment_id)
        .order_by(desc(EquipmentHealthIndex.ts))
        .limit(1)
    )
    return db.execute(stmt).scalars().first()

def get_latest_prediction(db: Session, equipment_id: int):
    stmt = (
        select(EquipmentPrediction)
        .where(EquipmentPrediction.equipment_id == equipment_id)
        .order_by(desc(EquipmentPrediction.ts))
        .limit(1)
    )
    return db.execute(stmt).scalars().first()
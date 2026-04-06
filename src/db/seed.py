from sqlalchemy.orm import Session
from src.db.models import Base, Equipment
from src.db.session import engine
from src.services.health_index import calculate_its
from src.db import crud

def init_db():
    Base.metadata.create_all(bind=engine)

def seed_demo(db: Session):
    # если уже есть данные — не дублируем
    if crud.list_equipment(db):
        return

    eq1 = Equipment(equipment_name="Генератор АБ4", equipment_type="Генератор", location="Цех 1", status="Работает")
    eq2 = Equipment(equipment_name="Насос N12", equipment_type="Насос", location="Цех 2", status="Работает")
    db.add_all([eq1, eq2])
    db.commit()

    # стартовые измерения
    for eq in [eq1, eq2]:
        m = crud.add_measurement(
            db,
            equipment_id=eq.equipment_id,
            temperature=45.0 if eq.equipment_id == eq1.equipment_id else 52.0,
            vibration=0.35 if eq.equipment_id == eq1.equipment_id else 0.55,
            operating_hours=3200.0 if eq.equipment_id == eq1.equipment_id else 6100.0,
            pressure=None,
        )

        its, parts = calculate_its(m.temperature, m.vibration, m.operating_hours)
        crud.save_health_index(db, eq.equipment_id, its, parts["s_temp"], parts["s_vib"], parts["s_hours"])

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
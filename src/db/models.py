from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Float, DateTime, Integer, func

class Base(DeclarativeBase):
    pass

class Equipment(Base):
    __tablename__ = "equipment"

    equipment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_name: Mapped[str] = mapped_column(String(200), nullable=False)
    equipment_type: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Работает")
    created_at: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now())

    measurements = relationship("EquipmentMeasurement", back_populates="equipment", cascade="all, delete-orphan")
    health = relationship("EquipmentHealthIndex", back_populates="equipment", cascade="all, delete-orphan")
    predictions = relationship("EquipmentPrediction", back_populates="equipment", cascade="all, delete-orphan")

class EquipmentMeasurement(Base):
    __tablename__ = "equipment_measurements"

    measurement_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.equipment_id"), index=True)

    ts: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now(), index=True)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    vibration: Mapped[float] = mapped_column(Float, nullable=False)
    operating_hours: Mapped[float] = mapped_column(Float, nullable=False)
    pressure: Mapped[float | None] = mapped_column(Float, nullable=True)

    equipment = relationship("Equipment", back_populates="measurements")

class EquipmentHealthIndex(Base):
    __tablename__ = "equipment_health_index"

    health_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.equipment_id"), index=True)

    ts: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now(), index=True)
    health_index: Mapped[float] = mapped_column(Float, nullable=False)  # 0..1

    temperature_score: Mapped[float] = mapped_column(Float, nullable=False)
    vibration_score: Mapped[float] = mapped_column(Float, nullable=False)
    hours_score: Mapped[float] = mapped_column(Float, nullable=False)

    equipment = relationship("Equipment", back_populates="health")

class EquipmentPrediction(Base):
    __tablename__ = "equipment_predictions"

    prediction_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.equipment_id"), index=True)

    ts: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now(), index=True)
    rul_days: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_failure_date: Mapped["DateTime"] = mapped_column(DateTime, nullable=False)

    failure_probability: Mapped[float | None] = mapped_column(Float, nullable=True)  # опционально
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, default="baseline-v1")

    equipment = relationship("Equipment", back_populates="predictions")

class EquipmentMLSample(Base):
    __tablename__ = "equipment_ml_samples"

    sample_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.equipment_id"), index=True)

    ts: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now(), index=True)

    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    vibration: Mapped[float] = mapped_column(Float, nullable=False)
    operating_hours: Mapped[float] = mapped_column(Float, nullable=False)
    pressure: Mapped[float | None] = mapped_column(Float, nullable=True)

    health_index: Mapped[float] = mapped_column(Float, nullable=False)
    rul_days: Mapped[int] = mapped_column(Integer, nullable=False)
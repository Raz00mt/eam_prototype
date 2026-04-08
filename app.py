import streamlit as st
from src.config import settings
from src.db.session import get_session
from src.db.seed import bootstrap
from src.db import crud
from src.services.health_index import (
    calculate_its,
    its_status,
    its_status_color,
    its_forecast_curve_variant_b,
)
from src.services.prediction import predict_rul_days, predict_failure_date
from src.ui.charts import plot_its_forecast

st.set_page_config(page_title="EAM MVP", layout="wide")

# Инициализация БД + демо-данные
bootstrap()

st.title("Мониторинг оборудования, ИТС и прогноз отказа")

db = get_session()
try:
    equipment_list = crud.list_equipment(db)
    if not equipment_list:
        st.warning("Нет оборудования в БД.")
        st.stop()

    # ===== Sidebar: выбор оборудования =====
    st.sidebar.header("Оборудование")
    names = [f"{e.equipment_name} ({e.equipment_type})" for e in equipment_list]
    idx = st.sidebar.selectbox("Выберите узел/оборудование", range(len(names)), format_func=lambda i: names[i])
    selected = equipment_list[idx]

    st.sidebar.caption(f"Локация: {selected.location or '—'}")
    st.sidebar.caption(f"Статус: {selected.status}")

    # ===== Main: 2 колонки =====
    col_left, col_right = st.columns([1.2, 1.8], gap="large")

    # ===== Получаем последние данные =====
    latest = crud.get_latest_measurement(db, selected.equipment_id)

    if latest is None:
        st.info("Нет измерений. Добавьте первое измерение.")
        st.stop()

    its, parts = calculate_its(latest.temperature, latest.vibration, latest.operating_hours)
    its_percent = its * 100
    status = its_status(its_percent)

    # базовый прогноз RUL (потом заменим на ML)
    rul_days = predict_rul_days(latest.temperature, latest.vibration, latest.operating_hours)
    failure_dt = predict_failure_date(rul_days)

    # ===== Левая колонка: карточка + редактирование =====
    with col_left:
        st.subheader("Карточка оборудования")
        st.write(f"**Наименование:** {selected.equipment_name}")
        st.write(f"**Тип:** {selected.equipment_type}")
        st.write(f"**Локация:** {selected.location or '—'}")

        st.divider()
        st.subheader("Текущие показатели")
        m1, m2, m3 = st.columns(3)
        m1.metric("Температура", f"{latest.temperature:.1f} °C")
        m2.metric("Вибрация", f"{latest.vibration:.2f}")
        m3.metric("Наработка", f"{latest.operating_hours:.0f} ч")

        st.divider()
        st.subheader("Ручное редактирование")
        with st.form("edit_form", clear_on_submit=False):
            t = st.number_input("Температура, °C", value=float(latest.temperature), step=0.5)
            v = st.number_input("Вибрация", value=float(latest.vibration), step=0.01, format="%.2f")
            h = st.number_input("Наработка, ч", value=float(latest.operating_hours), step=10.0)
            submitted = st.form_submit_button("Сохранить и пересчитать")

        if submitted:
            new_m = crud.add_measurement(db, selected.equipment_id, t, v, h, None)
            new_its, new_parts = calculate_its(new_m.temperature, new_m.vibration, new_m.operating_hours)
            crud.save_health_index(db, selected.equipment_id, new_its, new_parts["s_temp"], new_parts["s_vib"], new_parts["s_hours"])

            new_rul = predict_rul_days(new_m.temperature, new_m.vibration, new_m.operating_hours)
            new_fail = predict_failure_date(new_rul)
            crud.save_prediction(db, selected.equipment_id, new_rul, new_fail, None, model_version="baseline-v1")

            st.success("Сохранено. Обновляю панель…")
            st.rerun()

    # ===== Правая колонка: ИТС + прогноз + график =====
    with col_right:
        st.subheader("Панель состояния и прогноза")

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("ИТС", f"{its_percent:.1f}%")
        k3.metric("RUL", f"{rul_days} дней")
        k4.metric("Дата возможного отказа", failure_dt.strftime("%Y-%m-%d"))

        status_color = its_status_color(its_percent)
        with k2:
            st.markdown(
                f"""
                <div style="
                    background-color:{status_color};
                    color:white;
                    padding:16px;
                    border-radius:10px;
                    text-align:center;
                    font-weight:bold;
                    font-size:18px;
                ">
                    Статус<br>{status}
                </div>
                """,
                unsafe_allow_html=True
            )

        st.caption(f"Порог отказа: {settings.its_crit*100:.0f}% | Параметр деградации p={settings.degradation_p}")

        df = its_forecast_curve_variant_b(
            its0=its,
            its_crit=settings.its_crit,
            rul_days=rul_days,
            p=settings.degradation_p,
        )
        fig = plot_its_forecast(df, its_crit_percent=settings.its_crit * 100, failure_date=failure_dt)
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Расшифровка расчёта ИТС"):
            st.write(f"Температура score: **{parts['s_temp']:.3f}**")
            st.write(f"Вибрация score: **{parts['s_vib']:.3f}**")
            st.write(f"Наработка score: **{parts['s_hours']:.3f}**")

finally:
    db.close()
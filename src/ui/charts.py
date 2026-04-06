import plotly.graph_objects as go

def plot_its_forecast(df, its_crit_percent: float, failure_date):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["its_percent"],
        mode="lines",
        name="Прогноз ИТС"
    ))

    # Горизонтальная линия порога
    fig.add_hline(
        y=its_crit_percent,
        line_dash="dash",
        annotation_text=f"Порог {its_crit_percent:.0f}%"
    )

    # Вертикальная линия даты отказа через shape
    fig.add_shape(
        type="line",
        x0=failure_date,
        x1=failure_date,
        y0=0,
        y1=100,
        xref="x",
        yref="y",
        line=dict(dash="dash", width=2)
    )

    # Подпись к вертикальной линии
    fig.add_annotation(
        x=failure_date,
        y=95,
        text="Возможный отказ",
        showarrow=True,
        arrowhead=2,
        ax=40,
        ay=-40
    )

    fig.update_layout(
        xaxis_title="Дата",
        yaxis_title="ИТС, %",
        height=420,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    fig.update_yaxes(range=[0, 100])

    return fig
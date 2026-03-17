import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def build_risk_donut(label: str):
    categories = ["Stable", "Watch", "High Concern"]
    values = [1 if c == label else 0 for c in categories]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=categories,
                values=values,
                hole=0.65,
                textinfo="label",
                sort=False
            )
        ]
    )

    fig.update_layout(
        title="Environmental Risk Status",
        margin=dict(t=50, b=20, l=20, r=20),
        height=320,
        showlegend=True
    )

    return fig


def build_score_gauge(score: int):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Risk Score"},
            gauge={
                "axis": {"range": [0, 5]},
                "bar": {"thickness": 0.35},
                "steps": [
                    {"range": [0, 1], "color": "#d9f2d9"},
                    {"range": [1, 3], "color": "#fff2cc"},
                    {"range": [3, 5], "color": "#f4cccc"},
                ],
            },
        )
    )

    fig.update_layout(height=320, margin=dict(t=60, b=20, l=20, r=20))
    return fig


def build_indicator_bar(water_area_km2, rainfall_mm, ndvi_mean, ndci_mean):
    raw = {
        "Indicator": ["Water Area", "Rainfall", "NDVI", "NDCI Proxy"],
        "Value": [
            water_area_km2 if water_area_km2 is not None else 0,
            rainfall_mm if rainfall_mm is not None else 0,
            ndvi_mean if ndvi_mean is not None else 0,
            ndci_mean if ndci_mean is not None else 0,
        ],
    }

    df = pd.DataFrame(raw)
    max_val = df["Value"].max()
    df["Normalized"] = df["Value"] / max_val if max_val > 0 else 0
    df["LabelValue"] = df["Value"].round(3).astype(str)

    fig = px.bar(
        df,
        x="Indicator",
        y="Normalized",
        text="LabelValue",
        title="Normalized Indicator Comparison"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis_title="Relative Magnitude", xaxis_title="", height=360)
    return fig


def build_rainfall_bar(rainfall_df: pd.DataFrame, lake_name: str):
    df = rainfall_df.dropna(subset=["rainfall_mm"]).copy()

    if df.empty:
        return None

    fig = px.bar(
        df,
        x="date",
        y="rainfall_mm",
        title=f"Monthly Rainfall Around {lake_name}",
    )
    fig.update_layout(xaxis_title="Month", yaxis_title="Rainfall (mm)", height=420)
    return fig


def build_indicator_donut(water_area_km2, rainfall_mm, ndvi_mean, ndci_mean):
    values = [
        max(water_area_km2 or 0, 0),
        max(rainfall_mm or 0, 0),
        max(ndvi_mean or 0, 0),
        max(ndci_mean or 0, 0),
    ]
    labels = ["Water Area", "Rainfall", "NDVI", "NDCI Proxy"]

    if sum(values) == 0:
        values = [1, 1, 1, 1]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                textinfo="label+percent"
            )
        ]
    )

    fig.update_layout(
        title="Indicator Composition View",
        height=360,
        margin=dict(t=50, b=20, l=20, r=20)
    )
    return fig
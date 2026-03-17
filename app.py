import streamlit as st
import geemap.foliumap as geemap
import plotly.express as px

from src.ee_auth import initialize_earth_engine
from src.datasets import (
    get_lake_names,
    get_lake_by_name,
    get_sentinel2_collection,
    get_chirps_collection,
)
from src.analysis import (
    get_composite,
    add_indices,
    get_water_mask,
    get_lake_outline,
    calculate_band_mean,
    calculate_water_area_km2,
    calculate_total_rainfall_mm,
    build_monthly_rainfall_timeseries,
)
from src.risk import compute_risk_score
from src.charts import (
    build_risk_donut,
    build_score_gauge,
    build_indicator_bar,
    build_rainfall_bar,
    build_indicator_donut,
)

st.set_page_config(page_title="AquaTwin", layout="wide")

if "ee_initialized" not in st.session_state:
    initialize_earth_engine()
    st.session_state["ee_initialized"] = True


@st.cache_data
def get_lake_config_cached(name):
    return get_lake_by_name(name)


def run_analysis_for_lake(lake_name, start_date, end_date):
    lake_config = get_lake_config_cached(lake_name)

    waterbody = lake_config["waterbody"]
    aoi = lake_config["analysis_aoi"]
    zoom = lake_config["zoom"]

    s2 = get_sentinel2_collection(aoi, str(start_date), str(end_date))
    chirps = get_chirps_collection(aoi, str(start_date), str(end_date))

    composite = get_composite(s2)
    composite_with_indices = add_indices(composite)
    water_mask = get_water_mask(composite_with_indices, waterbody)
    lake_outline = get_lake_outline(waterbody, width=3)

    ndci_mean = calculate_band_mean(composite_with_indices, "NDCI_PROXY", waterbody, scale=30)
    ndvi_mean = calculate_band_mean(composite_with_indices, "NDVI", aoi, scale=30)
    water_area_km2 = calculate_water_area_km2(water_mask, waterbody, scale=30)
    rainfall_mm = calculate_total_rainfall_mm(chirps, aoi, scale=5000)

    rainfall_df = build_monthly_rainfall_timeseries(
        chirps_collection=chirps,
        geometry=aoi,
        start_date=str(start_date),
        end_date=str(end_date),
    )

    score, label, reasons = compute_risk_score(
        water_area_km2=water_area_km2,
        ndci_mean=ndci_mean,
        ndvi_mean=ndvi_mean,
        rainfall_mm=rainfall_mm,
    )

    return {
        "lake_name": lake_name,
        "start_date": start_date,
        "end_date": end_date,
        "selected_waterbody": waterbody,
        "selected_aoi": aoi,
        "zoom": zoom,
        "composite_with_indices": composite_with_indices,
        "water_mask": water_mask,
        "lake_outline": lake_outline,
        "ndci_mean": ndci_mean,
        "ndvi_mean": ndvi_mean,
        "water_area_km2": water_area_km2,
        "rainfall_mm": rainfall_mm,
        "rainfall_df": rainfall_df,
        "score": score,
        "label": label,
        "reasons": reasons,
    }


st.title("AquaTwin: Water Digital Twin Dashboard")
st.markdown(
    """
    A multi-lake water digital twin built with **Google Earth Engine + Streamlit + geemap**.

    It monitors:
    - Water extent
    - Water quality proxy
    - Surrounding vegetation condition
    - Rainfall pressure
    """
)

st.sidebar.header("Controls")

with st.sidebar.form("controls_form"):
    lake_name = st.selectbox("Select lake", get_lake_names())
    start_date = st.date_input("Start date")
    end_date = st.date_input("End date")
    selected_layer = st.selectbox(
        "Map layer",
        ["True Color", "NDWI", "Water Mask", "NDCI Proxy", "NDVI"]
    )
    run_button = st.form_submit_button("Run AquaTwin")

if run_button:
    with st.spinner("Running AquaTwin analysis..."):
        st.session_state["results"] = run_analysis_for_lake(
            lake_name=lake_name,
            start_date=start_date,
            end_date=end_date,
        )

if "results" in st.session_state:
    results = st.session_state["results"]

    st.subheader("Lake Condition Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Water Area (km²)", f"{results['water_area_km2']:,.2f}" if results["water_area_km2"] is not None else "N/A")
    c2.metric("NDCI Proxy Mean", f"{results['ndci_mean']:.3f}" if results["ndci_mean"] is not None else "N/A")
    c3.metric("Surrounding NDVI Mean", f"{results['ndvi_mean']:.3f}" if results["ndvi_mean"] is not None else "N/A")
    c4.metric("Total Rainfall (mm)", f"{results['rainfall_mm']:.2f}" if results["rainfall_mm"] is not None else "N/A")

    st.subheader("Risk and System Health")

    health_col1, health_col2 = st.columns(2)

    with health_col1:
        st.plotly_chart(build_risk_donut(results["label"]), width="stretch")

    with health_col2:
        st.plotly_chart(build_score_gauge(results["score"]), width="stretch")

    st.write(f"**Lake:** {results['lake_name']}")
    st.write(f"**Status:** {results['label']}")
    st.write(f"**Score:** {results['score']}")

    if results["reasons"]:
        st.write("**Why:**")
        for reason in results["reasons"]:
            st.write(f"- {reason}")
    else:
        st.write("No major warning signals detected in this prototype score.")

    st.subheader("Indicator Dashboard")

    dashboard_col1, dashboard_col2 = st.columns(2)

    with dashboard_col1:
        st.plotly_chart(
            build_indicator_bar(
                water_area_km2=results["water_area_km2"],
                rainfall_mm=results["rainfall_mm"],
                ndvi_mean=results["ndvi_mean"],
                ndci_mean=results["ndci_mean"],
            ),
            width="stretch",
        )

    with dashboard_col2:
        st.plotly_chart(
            build_indicator_donut(
                water_area_km2=results["water_area_km2"],
                rainfall_mm=results["rainfall_mm"],
                ndvi_mean=results["ndvi_mean"],
                ndci_mean=results["ndci_mean"],
            ),
            width="stretch",
        )

    st.subheader("Spatial Water State")

    map_col, info_col = st.columns([2, 1])

    with map_col:
        m = geemap.Map()
        m.centerObject(results["selected_waterbody"], results["zoom"])

        true_color_vis = {
            "bands": ["B4", "B3", "B2"],
            "min": 0.02,
            "max": 0.3,
        }
        ndwi_vis = {
            "min": -1,
            "max": 1,
            "palette": ["brown", "yellow", "blue"],
        }
        water_mask_vis = {"palette": ["0000FF"]}
        lake_outline_vis = {"palette": ["FF0000"]}
        ndci_vis = {
            "min": -0.2,
            "max": 0.4,
            "palette": ["purple", "white", "green"],
        }
        ndvi_vis = {
            "min": -1,
            "max": 1,
            "palette": ["brown", "yellow", "green"],
        }

        if selected_layer == "True Color":
            m.addLayer(results["composite_with_indices"].clip(results["selected_aoi"]), true_color_vis, "True Color")
        elif selected_layer == "NDWI":
            m.addLayer(results["composite_with_indices"].select("NDWI").clip(results["selected_waterbody"]), ndwi_vis, "NDWI")
        elif selected_layer == "Water Mask":
            m.addLayer(results["water_mask"], water_mask_vis, "Water Mask")
        elif selected_layer == "NDCI Proxy":
            m.addLayer(results["composite_with_indices"].select("NDCI_PROXY").clip(results["selected_waterbody"]), ndci_vis, "NDCI Proxy")
        elif selected_layer == "NDVI":
            m.addLayer(results["composite_with_indices"].select("NDVI").clip(results["selected_aoi"]), ndvi_vis, "NDVI")

        m.addLayer(results["lake_outline"], lake_outline_vis, "Lake Boundary")
        m.addLayerControl()
        m.to_streamlit(height=680)

    with info_col:
        st.markdown("### Map Notes")
        st.write("**Red outline:** official selected lake boundary")
        st.write("**Blue mask:** detected water inside the selected lake")
        st.write(f"**Current map layer:** {selected_layer}")
        st.write(f"**Analysis period:** {results['start_date']} to {results['end_date']}")

    st.subheader("Hydroclimatic Trend")

    rainfall_df = results["rainfall_df"]

    if not rainfall_df.empty:
        rainfall_bar_fig = build_rainfall_bar(rainfall_df, results["lake_name"])
        if rainfall_bar_fig is not None:
            st.plotly_chart(rainfall_bar_fig, width="stretch")

        rainfall_df_clean = rainfall_df.dropna(subset=["rainfall_mm"])
        if not rainfall_df_clean.empty:
            line_fig = px.line(
                rainfall_df_clean,
                x="date",
                y="rainfall_mm",
                markers=True,
                title=f"Monthly Rainfall Trend Around {results['lake_name']}"
            )
            line_fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Rainfall (mm)",
                height=420
            )
            st.plotly_chart(line_fig, width="stretch")

        with st.expander("Show rainfall data table"):
            st.dataframe(rainfall_df, width="stretch")
    else:
        st.info("No rainfall time series available for the selected period.")
else:
    st.info("Choose a lake, choose dates, then click Run AquaTwin.")
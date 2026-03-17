import ee
import geopandas as gpd
import json
import streamlit as st
from pathlib import Path

HYDROLAKES_PATH = Path("data/HydroLAKES_polys_v10.shp")

DEMO_LAKES = [
    "Victoria",
    "Naivasha",
    "Turkana",
    "Tanganyika",
    "Albert",
]


@st.cache_data
def load_hydrolakes():
    if not HYDROLAKES_PATH.exists():
        raise FileNotFoundError(
            f"HydroLAKES shapefile not found at: {HYDROLAKES_PATH}"
        )

    gdf = gpd.read_file(HYDROLAKES_PATH)

    if "Lake_name" not in gdf.columns:
        raise ValueError("Expected column 'Lake_name' not found in shapefile.")

    return gdf


@st.cache_data
def get_demo_lakes():
    gdf = load_hydrolakes().copy()
    gdf = gdf[gdf["Lake_name"].isin(DEMO_LAKES)].copy()
    gdf = gdf.dropna(subset=["Lake_name", "geometry"])
    return gdf


@st.cache_data
def get_lake_names():
    gdf = get_demo_lakes()
    return sorted(gdf["Lake_name"].unique().tolist())


def shapely_to_ee_geometry(shapely_geom):
    geojson = json.loads(gpd.GeoSeries([shapely_geom]).to_json())
    geometry = geojson["features"][0]["geometry"]
    return ee.Geometry(geometry)


def get_lake_by_name(lake_name):
    gdf = get_demo_lakes()
    row = gdf[gdf["Lake_name"] == lake_name]

    if row.empty:
        raise ValueError(f"Lake '{lake_name}' not found.")

    row = row.iloc[0]
    waterbody = shapely_to_ee_geometry(row.geometry)
    analysis_aoi = waterbody.buffer(20000)

    zoom_map = {
        "Victoria": 7,
        "Naivasha": 10,
        "Turkana": 8,
        "Tanganyika": 7,
        "Albert": 8,
    }

    return {
        "name": lake_name,
        "waterbody": waterbody,
        "analysis_aoi": analysis_aoi,
        "zoom": zoom_map.get(lake_name, 8),
    }


def get_sentinel2_collection(aoi, start_date, end_date):
    return (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    )


def get_chirps_collection(aoi, start_date, end_date):
    return (
        ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
    )
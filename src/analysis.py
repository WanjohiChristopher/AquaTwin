import ee
import pandas as pd


def mask_s2_clouds(image):
    qa = image.select("QA60")
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11

    mask = (
        qa.bitwiseAnd(cloud_bit_mask).eq(0)
        .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
    )

    return image.updateMask(mask).divide(10000)


def get_composite(collection):
    return collection.map(mask_s2_clouds).median()


def add_indices(image):
    ndwi = image.normalizedDifference(["B3", "B8"]).rename("NDWI")
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    ndci = image.normalizedDifference(["B5", "B4"]).rename("NDCI_PROXY")
    return image.addBands([ndwi, ndvi, ndci])

def get_water_mask(image, waterbody):

    ndwi = image.select("NDWI")
    ndvi = image.select("NDVI")

    water = ndwi.gt(0.1).And(ndvi.lt(0.1))

    water = water.clip(waterbody)

    water = water.focal_min(1).focal_max(1)

    return water.selfMask().rename("WaterMask")


def get_lake_outline(waterbody, width=3):
    return ee.Image().paint(waterbody, 1, width).selfMask().rename("LakeOutline")


def calculate_band_mean(image, band_name, geometry, scale=30):
    stat = image.select(band_name).reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=scale,
        maxPixels=1e13
    )
    value = stat.get(band_name)
    return value.getInfo() if value else None


def calculate_water_area_km2(water_mask, geometry, scale=30):
    pixel_area = ee.Image.pixelArea().divide(1e6)
    water_area = water_mask.multiply(pixel_area).reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=geometry,
        scale=scale,
        maxPixels=1e13
    )
    value = water_area.get("WaterMask")
    return value.getInfo() if value else None


def calculate_total_rainfall_mm(chirps_collection, geometry, scale=5000):
    rainfall_sum = chirps_collection.sum().rename("Rainfall")
    stat = rainfall_sum.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=scale,
        maxPixels=1e13
    )
    value = stat.get("Rainfall")
    return value.getInfo() if value else None


def build_monthly_rainfall_timeseries(chirps_collection, geometry, start_date, end_date):
    start = ee.Date(start_date)
    end = ee.Date(end_date)

    n_months = end.difference(start, "month").round()

    def make_monthly_feature(m):
        month_start = start.advance(m, "month")
        month_end = month_start.advance(1, "month")

        monthly_sum = (
            chirps_collection
            .filterDate(month_start, month_end)
            .sum()
            .rename("Rainfall")
        )

        stat = monthly_sum.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=5000,
            maxPixels=1e13
        )

        rainfall_value = ee.Algorithms.If(
            stat.contains("Rainfall"),
            stat.get("Rainfall"),
            None
        )

        return ee.Feature(
            None,
            {
                "date": month_start.format("YYYY-MM"),
                "rainfall_mm": rainfall_value
            }
        )

    months = ee.List.sequence(0, n_months.subtract(1))
    fc = ee.FeatureCollection(months.map(make_monthly_feature))
    features = fc.getInfo()["features"]

    records = []
    for feature in features:
        props = feature["properties"]
        records.append({
            "date": props.get("date"),
            "rainfall_mm": props.get("rainfall_mm"),
        })

    df = pd.DataFrame(records)

    if not df.empty:
        df["rainfall_mm"] = pd.to_numeric(df["rainfall_mm"], errors="coerce")

    return df
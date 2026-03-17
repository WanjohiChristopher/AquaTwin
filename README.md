# AquaTwin: Water Digital Twin Dashboard

AquaTwin is an interactive environmental monitoring system that creates a digital twin of lake ecosystems using satellite Earth observation data and cloud geospatial computing.

The system combines Google Earth Engine, Streamlit, and geospatial analytics to monitor lake conditions such as water extent, vegetation health, rainfall pressure, and potential ecological risk indicators.

Users can select a lake, choose an analysis time range, and visualize environmental indicators through interactive maps and dashboards.

The project demonstrates how Earth observation data can support water resource monitoring, environmental management, and climate resilience planning.



# Project Goals

The goal of AquaTwin is to demonstrate a lightweight digital twin architecture for freshwater monitoring using satellite data.

Key objectives include:

• Monitor lake surface water extent using satellite imagery  
• Estimate water quality proxy indicators  
• Monitor surrounding vegetation health  
• Analyze rainfall patterns affecting lake conditions  
• Generate environmental risk indicators  
• Provide an interactive geospatial dashboard



# Technology Stack

AquaTwin integrates several geospatial and cloud technologies.

Google Earth Engine  
Provides access to global satellite imagery datasets and large-scale geospatial computation.

Streamlit  
Provides a web-based interactive dashboard for users.

Geemap  
Provides map visualization tools for Earth Engine data in Python.

Plotly  
Used for charts, dashboards, and visual analytics.

Geopandas  
Used to load HydroLAKES shapefiles and convert geometries to Earth Engine format.

HydroLAKES Dataset  
Provides global lake polygon boundaries used as reference geometries.



# Satellite Datasets Used

Sentinel-2 Surface Reflectance

Sentinel-2 imagery is used for water detection, vegetation monitoring, and spectral index calculations.

Bands used include:

B2 – Blue  
B3 – Green  
B4 – Red  
B5 – Red Edge  
B8 – Near Infrared

Spectral indices calculated:

NDWI – water detection  
NDVI – vegetation health  
NDCI proxy – chlorophyll and algae indicator



CHIRPS Rainfall Dataset

The Climate Hazards Group InfraRed Precipitation with Station data (CHIRPS) dataset provides daily rainfall estimates derived from satellite imagery and weather station observations.

This dataset is used to estimate rainfall pressure affecting the lake ecosystem.



# System Architecture

The AquaTwin system consists of five main components.

Data Source Layer

Satellite imagery and climate data are accessed through Google Earth Engine.

Geospatial Processing Layer

Earth Engine performs:

satellite filtering  
cloud masking  
spectral index calculations  
water detection  
spatial statistics



Lake Geometry Layer

HydroLAKES shapefile provides lake boundaries used for:

lake selection  
analysis region definition  
map visualization



Analytics Layer

Python modules compute:

water extent  
vegetation indicators  
rainfall statistics  
environmental risk scoring



Visualization Layer

The Streamlit dashboard displays:

interactive maps  
environmental indicators  
rainfall charts  
risk assessment visualizations



# Project Structure

AquaTwin/

app.py  
Main Streamlit dashboard application

src/

ee_auth.py  
Google Earth Engine authentication module

datasets.py  
Lake geometry loading and dataset configuration

analysis.py  
Satellite image processing and environmental metrics

risk.py  
Environmental risk scoring logic

charts.py  
Dashboard charts and visualization utilities

data/

HydroLAKES shapefile files

requirements.txt  
Python dependencies

README.md  
Project documentation



# Key Environmental Metrics

Water Surface Area

Water extent is estimated using NDWI-based water detection within the lake polygon boundary.

NDWI thresholding identifies water pixels detected in Sentinel-2 imagery.



Vegetation Health

Vegetation health surrounding the lake is measured using NDVI calculated from Sentinel-2 imagery.

Low NDVI values may indicate degraded vegetation or environmental stress.



Chlorophyll Proxy

Chlorophyll concentration is approximated using a proxy derived from red-edge and red spectral bands.

Higher values may indicate increased algae concentrations.



Rainfall Pressure

Rainfall pressure is estimated using CHIRPS precipitation data aggregated over the analysis region.



# Environmental Risk Score

A rule-based environmental risk score is computed using:

water extent  
chlorophyll proxy  
vegetation health  
rainfall pressure



Risk Categories

Stable

Lake indicators appear within normal environmental ranges.

Watch

Early warning signals appear in one or more environmental indicators.

High Concern

Multiple indicators suggest ecological stress or environmental pressure.



# Map Visualization

The dashboard includes an interactive map displaying:

Lake boundary outline  
Detected water mask  
Satellite imagery layers

Users can switch between visualization layers:

True Color satellite imagery  
NDWI water detection  
NDVI vegetation index  
NDCI chlorophyll proxy  
Binary water mask



# Dashboard Visualizations

The dashboard includes several visual analytics components.

Risk Status Donut Chart  
Displays environmental risk category.

Risk Score Gauge  
Displays a numeric environmental score.

Indicator Comparison Bar Chart  
Compares normalized environmental indicators.

Indicator Composition Donut Chart  
Shows relative magnitude of environmental indicators.

Rainfall Time Series Chart  
Displays rainfall trends for the selected analysis period.



# Installation

Clone the repository

git clone https://github.com/yourusername/AquaTwin.git

cd AquaTwin



Create a virtual environment

python3 -m venv venv

source venv/bin/activate



Install dependencies

pip install -r requirements.txt



# Configure Earth Engine Authentication

Create a .env file in the project root.

Add the following environment variables:

EE_SERVICE_ACCOUNT=your-service-account@project.iam.gserviceaccount.com

EE_PROJECT_ID=your-earth-engine-project-id

EE_KEY_FILE=path/to/service_account_key.json



# Add HydroLAKES Data

Download the HydroLAKES lake polygon shapefile.

Place the following files inside the data directory:

data/HydroLAKES_polys_v10.shp  
data/HydroLAKES_polys_v10.dbf  
data/HydroLAKES_polys_v10.shx  
data/HydroLAKES_polys_v10.prj  



# Run the Application

Start the Streamlit server using the command below.

python3 -m streamlit run app.py



The application will launch in your browser at:

http://localhost:8501



# Performance Notes

The HydroLAKES shapefile is large (approximately 800MB). Streamlit caching is used to ensure the shapefile is loaded only once.

Earth Engine computations are executed server-side, reducing the computational load on the local machine.

Session state is used to prevent unnecessary recomputation when interacting with the dashboard.



# Future Improvements

Potential improvements for AquaTwin include:

real-time shoreline change detection  
lake water quality estimation using machine learning  
multi-lake comparison dashboards  
historical water level trend analysis  
automated anomaly detection  
integration with hydrological simulation models  
real-time monitoring pipelines



# License

This project uses the HydroLAKES dataset licensed under the Creative Commons Attribution 4.0 International License.




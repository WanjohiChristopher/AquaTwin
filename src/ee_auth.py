import ee
import os
from dotenv import load_dotenv

load_dotenv()


def initialize_earth_engine():
    service_account = os.getenv("EE_SERVICE_ACCOUNT")
    key_file = os.getenv("EE_KEY_FILE")
    project_id = os.getenv("EE_PROJECT_ID")

    if not service_account:
        raise ValueError("EE_SERVICE_ACCOUNT not found in environment variables")

    if not key_file:
        raise ValueError("EE_KEY_FILE not found in environment variables")

    if not project_id:
        raise ValueError("EE_PROJECT_ID not found in environment variables")

    if not os.path.exists(key_file):
        raise FileNotFoundError(f"Service account key file not found: {key_file}")

    credentials = ee.ServiceAccountCredentials(service_account, key_file)
    ee.Initialize(credentials, project=project_id)
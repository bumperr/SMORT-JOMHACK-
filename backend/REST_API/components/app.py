from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from database import Database
from smortPredictor import smortPredictorImplementor
from os import getenv
from dotenv import load_dotenv
from pathlib import Path

import optimize_collection
from pydantic import BaseModel
from fastapi import status

class DriverLocationInput(BaseModel):
    latitude: str
    longitude: str
    region_id: int

class OptimizationResponse(BaseModel):
    status: str
    message: str
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
env_path = Path(__file__).resolve().parents[3] / '.env'
load_dotenv(dotenv_path=env_path)


db = Database(getenv("DB_HOST"), getenv("DB_PORT"), getenv(
    "DB_USER"), getenv("DB_PASSWORD"), getenv("DB_NAME"))


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/region")
async def get_regions():
    regions = await db.get_regions()
    return regions


@app.get("/region/{region_ID}/sensors")
async def get_region_sensors(region_ID: int):
    sensors = await db.get_region_sensors(region_ID)
    return sensors


@app.post("/sensor")
async def add_sensor(data: dict):
    status = await db.add_sensor(**data)
    if not status:
        return HTTPException(status_code=422, detail="Maybe the JSON data is wrong...")
    return status


@app.get("/sensor/{sensor_ID}")
async def get_sensor(sensor_ID: int):
    sensor = await db.get_sensor(sensor_ID)
    return sensor


@app.get("/sensor/{sensor_ID}/record")
async def get_latest_sensor_trash_level(sensor_ID: int):
    record = await db.get_latest_sensor_trash_level(sensor_ID)
    return record


@app.get("/sensor/{sensor_ID}/records")
async def get_sensor_records(sensor_ID: int):
    records = await db.get_sensor_records(sensor_ID)
    return records


@app.post("/record")
async def create_sensor_record(sensor_data: dict):
    status = await db.add_sensor_record(**sensor_data)
    if not status:
        return HTTPException(status_code=422, detail="Maybe the JSON data is wrong...")
    return status


@app.get("/predict/{sensor_id}")
async def predict(sensor_id: int):
    predictor = smortPredictorImplementor(model_directory=None)
    prediction = await predictor.predict_full_level(sensor_id)

    return prediction


@app.get("/analytics/level/{region_id}")
async def get_latest_trash_levels_in_region(region_id: int):
    trash_levels = await db.get_latest_trash_levels_in_region(region_id)
    return trash_levels


@app.get("/analytics/average/all")
async def get_average_trash_levels_all_sensors():
    average_trash_levels = await db.get_average_trash_levels_all_sensors()
    return average_trash_levels


@app.get("/analytics/average/{region_id}")
async def get_average_trash_levels_of_all_sensors_in_region(region_id: int):
    average_trash_levels = await db.get_average_trash_levels_all_sensors_in_region(region_id)
    return average_trash_levels

#prince part 

@app.post("/driverLocation", response_model=OptimizationResponse)
async def add_driver_location(data: DriverLocationInput):
    """
    Input JSON should be like:
    {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "region_id": 1
    }

    Response example:
    {
        "status": "400",
        "message": "https://maps/link/api ............"
    }
    """
    frequency = 24  # hours
    start_time_string = "2024-01-01 08:00:00"

    collection_origin = f"{data.latitude},{data.longitude}"  # Corrected to use the fields properly

    refered_date_string = "2025-04-26 22:00:00"  # Example 'now'
    
    target_region_id = data.region_id  # Region ID comes from request
    
    try:
        link = await optimize_collection.main(frequency, start_time_string, collection_origin, target_region_id, refered_date_string)
    except Exception as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    
    return {
        "status": "200",
        "message": link
    }

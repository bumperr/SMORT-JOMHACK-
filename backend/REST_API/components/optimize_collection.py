import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from dotenv import load_dotenv
import os
from pathlib import Path

from database import Database
from router import router
from smortPredictor import smortPredictorImplementor

# Constants
CONFIDENCE_THRESHOLD = 0.75  # Only accept predictions above 75% confidence
BUFFER_HOURS = 0.2  # Safety margin before bin is fully full

# Setup environment once
load_dotenv()

async def get_sensors_for_collection(
    frequency_hours: int,
    start_time: datetime,
    region_id: int,
    refered_date: Optional[datetime] = None
) -> List[Dict]:
    """
    Returns bins that will be full before next scheduled collection.
    """

    if refered_date is None:
        refered_date = datetime.now()

    db = Database(
        os.getenv("DB_HOST"),
        os.getenv("DB_PORT"),
        os.getenv("DB_USER"),
        os.getenv("DB_PASSWORD"),
        os.getenv("DB_NAME")
    )
    
    if not db.check_connection():
        print("Error: Database connection failed.")
        return []

    sensors_for_collection = []
    predictor = smortPredictorImplementor()

    try:
        sensors = await db.get_region_sensors(region_id)  # Fetch sensors in the region

        for sensor in sensors:
            sensor_id = sensor[0]
            latitude = sensor[1]
            longitude = sensor[2]

            # Calculate next scheduled collection time
            next_collection_time = start_time
            
            if next_collection_time < refered_date:
                diff_hours = (refered_date - next_collection_time).total_seconds() / 3600
                skips = (diff_hours // frequency_hours) + 1
                next_collection_time += timedelta(hours=skips * frequency_hours)

            print(next_collection_time)
            prediction = await predictor.predict_full_level(sensor_id)
            if prediction:
                hours_until_full = prediction["hours_until_full"]
                time_full = refered_date + timedelta(hours=hours_until_full)
                print(f"Sensor {sensor_id} will be full at {time_full} " ,f"which is {hours_until_full:.2f} hours away.")
                
                # Apply buffer
                adjusted_time_full = time_full - timedelta(hours=BUFFER_HOURS)

                # Decision: urgent if it will overflow (with buffer) before next pickup
                print("adjusted_time_full: {adjusted_time_full} , next_collection : {next_collection_time}")
                if adjusted_time_full <= next_collection_time:
                    sensors_for_collection.append({
                        "id": sensor_id,
                        "latitude": latitude,
                        "longitude": longitude
                    })
            else:
                print(f"Warning: No prediction for sensor {sensor_id}. Skipping.")
    
    finally:
        db.close_connection()

    return sensors_for_collection

async def generate_optimized_route(sensors: List[Dict], origin: str) -> Optional[str]:
    """
    Generate an optimized multi-stop Google Maps URL from selected sensors.
    """
    if not sensors:
        return None

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    route_optimizer = router(api_key)

    coordinates_json = json.dumps([
    {"latitude": float(s["latitude"]), "longitude": float(s["longitude"])}
    for s in sensors
    ])

    # Sort the coordinates to minimize travel distance
    optimized_json = route_optimizer.sorting_waypoints(
        coordinates_json, origin,
        EmissionRatePerKM=0.1, FuelConsumptionRatePerKM=0.1
    )

    # Generate final Google Maps route URL
    final_url = route_optimizer.generate_multi_stop_url(optimized_json, origin)
    return final_url

async def main(
    frequency_hours: int,
    start_time_str: str,
    origin: str,
    region_id: int,
    refered_date_str: str
): 
    try:
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
        refered_date = datetime.strptime(refered_date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print(f"Error: Invalid date format: {e}. Use YYYY-MM-DD HH:MM:SS format.")
        return

    sensors_to_collect = await get_sensors_for_collection(
        frequency_hours, start_time, region_id, refered_date
    )

    if sensors_to_collect:
        print(f"Sensors needing collection in region {region_id}:")
        for s in sensors_to_collect:
            print(f" - ID {s['id']}: ({s['latitude']}, {s['longitude']})")
        
        route_url = await generate_optimized_route(sensors_to_collect, origin)
        
        if route_url:
            print("\nOptimized Google Maps Route URL:")
            print(route_url)

            return route_url
        else:
            print("\nError: Could not generate route.")
    else:
        print("\nNo bins require urgent collection at this time.")

    
    return None

if __name__ == "__main__":
    frequency = 24  # hours
    start_time_string = "2024-01-01 08:00:00"
    collection_origin = "4.361614918423233, 100.9688357519585"  # Example origin:SI
    refered_date_string = "2025-04-26 22:00:00"  # Example 'now'
    target_region_id = 1  # Region ID

    asyncio.run(main(frequency, start_time_string, collection_origin, target_region_id,refered_date_string))

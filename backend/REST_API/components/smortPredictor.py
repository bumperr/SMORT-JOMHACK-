import os
import joblib
import pandas as pd
import os
from typing import Dict
from database import  Database
from dotenv import load_dotenv
from pathlib import Path
import asyncio 

class SmortPredictor:
    def __init__(self, model_dir: str, sensor_ids: list):

        self.model_dir = model_dir
        self.sensors = sensor_ids
        self.models = self.load_models()

    def load_models(self) -> Dict[int, joblib]:
        models = {}
        for sensor_id in self.sensors:
            model_path = os.path.join(
                self.model_dir, f"sensor_{sensor_id}_model.joblib")
            #print(f"model path: {model_path} loaded")
            if os.path.exists(model_path):
                models[sensor_id] = joblib.load(model_path)
            else:
                print(f"Warning: Model file not found for sensor {sensor_id}")
        return models

    def predict_full_level(self, sensor_id: int, latest_data: Dict):
        if sensor_id not in self.models:
            raise ValueError(f"Model for sensor {sensor_id} is not loaded.")

        model = self.models[sensor_id]
        last_timestamp = latest_data['time_stamp']
        current_data = latest_data.copy()

        for step in range(672):
            features = {
                'hour': (last_timestamp + pd.Timedelta(minutes=(step + 1) * 15)).hour,
                'day_of_week': (last_timestamp + pd.Timedelta(minutes=(step + 1) * 15)).dayofweek,
                'month': (last_timestamp + pd.Timedelta(minutes=(step + 1) * 15)).month,
                'is_weekend': int((last_timestamp + pd.Timedelta(minutes=(step + 1) * 15)).dayofweek in [5, 6]),
                'lag_1': current_data['trash_level'],
                'lag_2': current_data['lag_1'],
                'lag_3': current_data['lag_2']
            }

            pred = model.predict(pd.DataFrame([features]))[0]

            current_data['lag_3'] = current_data['lag_2']
            current_data['lag_2'] = current_data['lag_1']
            current_data['lag_1'] = pred
            current_data['trash_level'] = pred

            if pred >= 90:
                predicted_time = last_timestamp + \
                    pd.Timedelta(minutes=(step + 1) * 15)
                return {
                    'sensor_id': sensor_id,
                    'predicted_timestamp': predicted_time,
                    'hours_until_full': (step + 1) * 0.25,
                    'predicted_level': pred
                }

        return None


class smortPredictorImplementor:
    def __init__(self, model_directory=None, sensor_ids=[1, 2, 3, 4, 5, 6, 7, 8, 9]):
        if model_directory is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_directory = os.path.abspath(os.path.join(base_dir, '..', 'ML-model'))

        self.model_directory = model_directory
        self.sensor_ids = sensor_ids
        self.predictor = SmortPredictor(self.model_directory, self.sensor_ids)

    async def predict_full_level(self, sensor_id: int):
        env_path = Path(__file__).resolve().parents[3] / '.env'
        load_dotenv(dotenv_path=env_path)
        db = Database(os.getenv("DB_HOST"), os.getenv("DB_PORT"), os.getenv(
            "DB_USER"), os.getenv("DB_PASSWORD"), os.getenv("DB_NAME"))

        latest_data = await db.get_latest_sensor_record(
            sensor_ID=sensor_id, num_of_row=4)

        data = {
            # Most recent timestamp
            'time_stamp': pd.Timestamp(latest_data[0][1]),
            'trash_level': float(latest_data[0][2]),        # Current level
            'lag_1': float(latest_data[1][2]),             # Previous reading
            'lag_2': float(latest_data[2][2]),             # Two readings ago
            'lag_3': float(latest_data[3][2])              # Three readings ago

        }

        # dictionary cotained predicted_timestamp, hours_until_full, predicted_level
        return self.predictor.predict_full_level(sensor_id, data)


if __name__ == "__main__":
    # example of predicting sensor 9

    # +++++++++++++++++=Predict for sensor 9+++++++++++
    obj = smortPredictorImplementor()
    sensor_id = 9

    full_prediction = asyncio.run (obj.predict_full_level(sensor_id))

    if full_prediction:
        print(
            f"Sensor {sensor_id} - Trash will be full at: {full_prediction['predicted_timestamp']}")
        print(f"Hours until full: {full_prediction['hours_until_full']}")
        print(f"Predicted level: {full_prediction['predicted_level']:.2f}%")
    else:
        print(
            f"Sensor {sensor_id} - No full-level prediction found within the next 7 days.")
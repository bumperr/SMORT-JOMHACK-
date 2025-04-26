import asyncio
import os
from pathlib import Path
import joblib
import logging
from datetime import datetime
from dotenv import load_dotenv

from database import Database
from randomForest import SmortML  

# Setup logging
def setup_logging():
    logs_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f"train_sensors_{now}.log")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Optional: Also print to console
        ]
    )

    logging.info(f"Logging started. Output file: {log_file}")

async def train_sensor(sensor_id: int, db: Database, model_save_path: str):
    data = await db.get_partial_sensor_record(sensor_id)
    
    if not data:
        logging.warning(f"No data found for sensor {sensor_id}. Skipping...")
        return

    model = SmortML(data)
    model.clean_data()
    model.extract_features()
    model.split_train_test(test_size=0.2)
    model.train_random_forest()
    #log for model evaluation
    mae, rmse, r2 = model.evaluate_model()
    logging.info(f"[Sensor {sensor_id}] MAE: {mae:.2f}, RMSE: {rmse:.2f}, R²: {r2:.2f}")
    
    # Log K-Fold Cross Validation
    mean_mae, std_mae = model.k_fold_cross_validation(k=5)
    logging.info(f"[Sensor {sensor_id}] K-Fold Mean MAE: {mean_mae:.2f}, Standard Deviation: {std_mae:.2f}")

    full_prediction = model.predict_full_level()
    if full_prediction:
        logging.info(f"[Sensor {sensor_id}] Trash will be full at: {full_prediction['predicted_timestamp']}")
        logging.info(f"[Sensor {sensor_id}] Hours until full: {full_prediction['hours_until_full']}")
        logging.info(f"[Sensor {sensor_id}] Predicted level: {full_prediction['predicted_level']:.2f}%")
    else:
        logging.warning(f"[Sensor {sensor_id}] No full-level prediction found within the next 2 days.")
    model_file = os.path.join(model_save_path, f"sensor_{sensor_id}_model.joblib")
    joblib.dump(model.model, model_file)
    logging.info(f"[Sensor {sensor_id}] Model saved successfully at: {model_file}")

async def main():
    # Setup logging first
    setup_logging()

    # Load environment
    env_path = Path(__file__).resolve().parents[3] / '.env'
    load_dotenv(dotenv_path=env_path)

    # Connect to DB
    db = Database(
        os.getenv("DB_HOST"),
        os.getenv("DB_PORT"),
        os.getenv("DB_USER"),
        os.getenv("DB_PASSWORD"),
        os.getenv("DB_NAME")
    )

    # Create model directory if it doesn't exist
    model_save_path = os.path.join(os.getcwd(), "ML-model")
    os.makedirs(model_save_path, exist_ok=True)

    try:
        # Loop over sensors 1 to 9
        for sensor_id in range(1, 10):
            logging.info(f"\n=== Training Sensor {sensor_id} ===")
            await train_sensor(sensor_id, db, model_save_path)

    finally:
        db.close_connection()
        logging.info("Database connection closed.")

if __name__ == "__main__":
    asyncio.run(main())

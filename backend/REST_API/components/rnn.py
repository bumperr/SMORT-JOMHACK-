import pandas as pd
import numpy as np
from typing import List, Tuple, Optional
import datetime
from decimal import Decimal
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import KFold
from sklearn.exceptions import NotFittedError
from database import Database
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score 
import joblib
import os
from dotenv import load_dotenv
from pathlib import Path
import asyncio 
from tensorflow.keras.models import Sequential, save_model
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping

class SmortML:
    def __init__(self, data: List[Tuple[int, datetime.datetime, Decimal]]):
        self.data = self.convert_data_to_df(data)
        self.model = None
        self.predictions = None
        self.sequence_length = 24  # Using 6 hours of history (24 15-minute intervals)
        self.feature_columns = ['hour', 'day_of_week', 'month', 'is_weekend', 'trash_level']
        self.X = None
        self.y = None
        
    def convert_data_to_df(self, data) -> pd.DataFrame:
        try:
            df = pd.DataFrame(data, columns=['smort_ID', 'time_stamp', 'trash_level'])
            df['trash_level'] = df['trash_level'].astype(float)
            if df.empty:
                raise ValueError("Empty dataset provided")
            return df
        except Exception as e:
            raise ValueError(f"Error converting data to DataFrame: {str(e)}")

    def clean_data(self) -> None:
        try:
            self.data['time_stamp'] = pd.to_datetime(self.data['time_stamp'])
            self.data = self.data.sort_values(by='time_stamp')
            
            # Resample and fill missing values
            self.data = self.data.set_index('time_stamp').resample('15T').ffill().reset_index()
            self.data['trash_level'] = self.data['trash_level'].interpolate()
            
            # Handle outliers
            Q1 = self.data['trash_level'].quantile(0.25)
            Q3 = self.data['trash_level'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            mask = (self.data['trash_level'] < lower_bound) | (self.data['trash_level'] > upper_bound)
            self.data.loc[mask, 'trash_level'] = np.nan
            self.data['trash_level'] = self.data['trash_level'].ffill().bfill()
            
        except Exception as e:
            raise ValueError(f"Error cleaning data: {str(e)}")

    def extract_features(self) -> None:
        try:
            # Create time-based features
            self.data['hour'] = self.data['time_stamp'].dt.hour
            self.data['day_of_week'] = self.data['time_stamp'].dt.dayofweek
            self.data['month'] = self.data['time_stamp'].dt.month
            self.data['is_weekend'] = self.data['day_of_week'].isin([5, 6]).astype(int)
            
            # Create sequences for LSTM
            features = self.data[self.feature_columns].values
            X, y = [], []
            
            for i in range(len(features) - self.sequence_length):
                X.append(features[i:i+self.sequence_length])
                y.append(features[i+self.sequence_length, -1])  # Predict next trash_level
                
            self.X = np.array(X)
            self.y = np.array(y)
            
        except Exception as e:
            raise ValueError(f"Error extracting features: {str(e)}")

    def split_train_test(self, test_size: float = 0.2, random_state: int = 42):
        try:
            # Time-series split (maintain temporal order)
            split_idx = int(len(self.X) * (1 - test_size))
            self.X_train, self.y_train = self.X[:split_idx], self.y[:split_idx]
            self.X_test, self.y_test = self.X[split_idx:], self.y[split_idx:]
            
            print(f"Training set size: {len(self.X_train)}")
            print(f"Testing set size: {len(self.X_test)}")
        except Exception as e:
            raise ValueError(f"Error splitting data: {str(e)}")

    def train_random_forest(self):
        try:
            if not hasattr(self, 'X_train'):
                raise ValueError("Training data not found. Call split_train_test() first.")
            
            # LSTM Model
            self.model = Sequential([
                LSTM(64, input_shape=(self.sequence_length, len(self.feature_columns)), 
                    return_sequences=True),
                LSTM(32),
                Dense(1)
            ])
            
            self.model.compile(optimizer='adam', loss='mse')
            
            # Add early stopping
            early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
            
            self.model.fit(
                self.X_train, self.y_train,
                epochs=100,
                batch_size=32,
                validation_split=0.2,
                callbacks=[early_stop],
                verbose=1
            )
            print("RNN model trained successfully.")
        except Exception as e:
            raise ValueError(f"Error training model: {str(e)}")

    def evaluate_model(self):
        if self.model is None:
            raise NotFittedError("Model not fitted. Call train_random_forest() first.")
            
        try:
            y_pred = self.model.predict(self.X_test).flatten()
            mae = mean_absolute_error(self.y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(self.y_test, y_pred))
            r2 = r2_score(self.y_test, y_pred)

            print(f"Test Set Evaluation:")
            print(f"MAE: {mae:.2f}")
            print(f"RMSE: {rmse:.2f}")
            print(f"R²: {r2:.2f}")
            return mae, rmse, r2
        except Exception as e:
            raise ValueError(f"Error evaluating model: {str(e)}")

    def predict_full_level(self, threshold=95, max_steps=1000) -> Optional[datetime.datetime]:
        if self.model is None:
            raise NotFittedError("Model not fitted. Call train_random_forest() first.")
            
        try:
            current_sequence = self.X[-1]  # Most recent sequence
            last_timestamp = self.data['time_stamp'].iloc[-1]
            
            for step in range(max_steps):
                # Predict next value
                pred = self.model.predict(current_sequence[np.newaxis, ...])[0][0]
                
                if pred >= threshold:
                    predicted_time = last_timestamp + pd.Timedelta(minutes=(step+1)*15)
                    return {
                        'predicted_timestamp': predicted_time,
                        'hours_until_full': (step+1)*0.25,
                        'predicted_level': pred
                    }
                
                # Generate new features for next timestep
                new_time = last_timestamp + pd.Timedelta(minutes=(step+1)*15)
                new_features = [
                    new_time.hour,
                    new_time.dayofweek,
                    new_time.month,
                    1 if new_time.dayofweek in [5, 6] else 0,
                    pred
                ]
                
                # Update sequence
                current_sequence = np.roll(current_sequence, -1, axis=0)
                current_sequence[-1] = new_features
                
            return None
        except Exception as e:
            raise ValueError(f"Error predicting full level: {str(e)}")

    def k_fold_cross_validation(self, k: int = 5):
        try:
            # Time-series aware cross-validation
            fold_size = len(self.X) // k
            scores = []
            
            for i in range(k):
                val_start = i * fold_size
                val_end = (i+1) * fold_size
                
                X_train = np.concatenate([self.X[:val_start], self.X[val_end:]], axis=0)
                y_train = np.concatenate([self.y[:val_start], self.y[val_end:]], axis=0)
                X_val = self.X[val_start:val_end]
                y_val = self.y[val_start:val_end]
                
                model = Sequential([
                    LSTM(32, input_shape=(self.sequence_length, len(self.feature_columns))),
                    Dense(1)
                ])
                model.compile(optimizer='adam', loss='mse')
                model.fit(X_train, y_train, epochs=20, verbose=0)
                
                score = model.evaluate(X_val, y_val, verbose=0)
                scores.append(score)
                
            mean_score = np.mean(scores)
            std_score = np.std(scores)
            
            print(f"K-Fold Cross-Validation Results (k={k}):")
            print(f"Mean MSE: {mean_score:.2f}")
            print(f"Standard Deviation: {std_score:.2f}")
            return mean_score, std_score
            
        except Exception as e:
            raise ValueError(f"Error during cross-validation: {str(e)}")

if __name__ == "__main__":
    env_path = Path(__file__).resolve().parents[3] / '.env'
    load_dotenv(dotenv_path=env_path)
   
    sensor=7

    db = Database(os.getenv("DB_HOST"), os.getenv("DB_PORT"), os.getenv(
        "DB_USER"), os.getenv("DB_PASSWORD"), os.getenv("DB_NAME"))
    
    data = asyncio.run(db.get_partial_sensor_record(sensor))
    model = SmortML(data)
    model.clean_data()
    model.extract_features()

    model.split_train_test(test_size=0.2)
    model.train_random_forest()
    model.evaluate_model()
    model.k_fold_cross_validation(k=5)

    full_prediction = model.predict_full_level()
    if full_prediction:
        print(f"Trash will be full at: {full_prediction['predicted_timestamp']}")
        print(f"Hours until full: {full_prediction['hours_until_full']}")
        print(f"Predicted level: {full_prediction['predicted_level']:.2f}%")

    # Save Keras model
    current_dir = os.getcwd()
    model_file = os.path.join(current_dir, f"sensor_{sensor}_rnn_model.keras")
    model.model.save(model_file)
    print(f"Model saved successfully at: {model_file}")
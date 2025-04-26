import pandas as pd
import numpy as np
from typing import List, Tuple, Optional
import datetime
from decimal import Decimal
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import KFold
from sklearn.exceptions import NotFittedError
from sklearn.model_selection import train_test_split
from database import Database
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_score
from sklearn.metrics import r2_score 
import joblib
import os
from dotenv import load_dotenv
from pathlib import Path
import asyncio 
class SmortML:
    def __init__(self, data: List[Tuple[int, datetime.datetime, Decimal]]):
        self.data = self.convert_data_to_df(data)
        self.model = None
        self.predictions = None
        
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
            
            
            self.data = self.data.set_index('time_stamp').resample('15min').ffill().reset_index()
            self.data['trash_level'] = self.data['trash_level'].ffill()
            if self.data['trash_level'].isna().any():
                self.data['trash_level'] = self.data['trash_level'].bfill()
                
            # Handle outliers
            Q1 = self.data['trash_level'].quantile(0.25)
            Q3 = self.data['trash_level'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            mask = (self.data['trash_level'] < lower_bound) | (self.data['trash_level'] > upper_bound)
            self.data.loc[mask, 'trash_level'] = np.nan
            self.data['trash_level'] = self.data['trash_level'].interpolate()
            
        except Exception as e:
            raise ValueError(f"Error cleaning data: {str(e)}")

    def extract_features(self) -> None:
        try:
            self.data['hour'] = self.data['time_stamp'].dt.hour
            self.data['day_of_week'] = self.data['time_stamp'].dt.dayofweek
            self.data['month'] = self.data['time_stamp'].dt.month
            self.data['is_weekend'] = self.data['day_of_week'].isin([5, 6]).astype(int)
            
            # Lag features for time series
            self.data['lag_1'] = self.data['trash_level'].shift(1)
            self.data['lag_2'] = self.data['trash_level'].shift(2)
            self.data['lag_3'] = self.data['trash_level'].shift(3)
         
            self.data = self.data.dropna()
        except Exception as e:
            raise ValueError(f"Error extracting features: {str(e)}")

   

    def predict_full_level(self, threshold=95, step_minutes=30) -> dict:
        if self.model is None:
            raise NotFittedError("Model not fitted. Call train_random_forest() first.")
            
        try:
            last_timestamp = self.data['time_stamp'].iloc[-1]
            current_data = self.data.iloc[-1].copy()
            step = 0
            
            while True:
                future_time = last_timestamp + pd.Timedelta(minutes=(step + 1) * step_minutes)
                features = {
                    'hour': future_time.hour,
                    'day_of_week': future_time.dayofweek,
                    'month': future_time.month,
                    'is_weekend': int(future_time.dayofweek in [5, 6]),
                    'lag_1': current_data['trash_level'],
                    'lag_2': current_data['lag_1'],
                    'lag_3': current_data['lag_2']
                }
                
                pred = self.model.predict(pd.DataFrame([features]))[0]
                
                # Update lags
                current_data['lag_3'] = current_data['lag_2']
                current_data['lag_2'] = current_data['lag_1']
                current_data['lag_1'] = pred
                current_data['trash_level'] = pred
                
                step += 1  # Move to next step
                
                if pred >= threshold:
                    return {
                        'predicted_timestamp': future_time,
                        'hours_until_full': step * (step_minutes / 60),
                        'predicted_level': pred
                    }
            
        except Exception as e:
            raise ValueError(f"Error predicting full level: {str(e)}")

#-----------------------verification--------------------------------------------

    def split_train_test(self, test_size: float = 0.2, random_state: int = 42):
        try:
            features = ['hour', 'day_of_week', 'month', 'is_weekend', 'lag_1', 'lag_2', 'lag_3']
            X = self.data[features]
            y = self.data['trash_level']
            
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            print(f"Training set size: {len(self.X_train)}")
            print(f"Testing set size: {len(self.X_test)}")
        except Exception as e:
            raise ValueError(f"Error splitting data into train and test sets: {str(e)}")
      

    def train_random_forest(self):
        
        try:
            if not hasattr(self, 'X_train') or not hasattr(self, 'y_train'):
                raise ValueError("Training data not found. Call split_train_test() first.")
            

            self.model = RandomForestRegressor(n_estimators=250, max_depth=5, min_samples_split=10,min_samples_leaf=10,random_state=42)
            self.model.fit(self.X_train, self.y_train)
            print("Random Forest model trained successfully.")
        except Exception as e:
            raise ValueError(f"Error training Random Forest model: {str(e)}")

    def evaluate_model(self):
        if self.model is None:
            raise NotFittedError("Model not fitted. Call train_random_forest() first.")
            
        try:
            y_pred = self.model.predict(self.X_test)
            mae = mean_absolute_error(self.y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(self.y_test, y_pred))
            r2 = r2_score(self.y_test, y_pred)  

            print(f"Test Set Evaluation:")
            print(f"MAE: {mae:.2f}")
            print(f"RMSE: {rmse:.2f}")
            print(f"R²: {r2:.2f}")  

            return mae, rmse, r2  # ✅ Added return statement
        except Exception as e:
            raise ValueError(f"Error evaluating model: {str(e)}")


    def k_fold_cross_validation(self, k: int = 5):
        try:
            features = ['hour', 'day_of_week', 'month', 'is_weekend', 'lag_1', 'lag_2', 'lag_3']
            X = self.data[features]
            y = self.data['trash_level']
            
            kf = KFold(n_splits=k, shuffle=True, random_state=42)
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            # Perform cross-validation
            scores = cross_val_score(model, X, y, cv=kf, scoring='neg_mean_absolute_error')
            scores = -scores  # Convert to positive MAE
            mean_mae = scores.mean()
            std_mae = scores.std()

            print(f"K-Fold Cross-Validation Results (k={k}):")
            print(f"Mean MAE: {mean_mae:.2f}")
            print(f"Standard Deviation: {std_mae:.2f}")

            return mean_mae, std_mae  # Added return statement
        except Exception as e:
            raise ValueError(f"Error performing k-fold cross-validation: {str(e)}")

    

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


    current_dir = os.getcwd()  


    
    model_file = os.path.join(current_dir, f"sensor_{sensor}_model.joblib")

    joblib.dump(model.model, model_file)  

    print(f"Model saved successfully at: {model_file}")
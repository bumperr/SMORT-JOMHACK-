import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from io import StringIO

def sql_to_dataframe(sql_file_path):
    """Convert SQL INSERT statements to a pandas DataFrame"""
    data = []
    pattern = re.compile(r"INSERT INTO sensor_record \(smort_ID, time_stamp, trash_level, image\) VALUES \('(\d+)', '([^']+)', (\d+), ''\);")
    
    with open(sql_file_path, 'r') as file:
        for line in file:
            match = pattern.match(line.strip())
            if match:
                sensor_id, timestamp, trash_level = match.groups()
                data.append({
                    'sensor_id': int(sensor_id),
                    'timestamp': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
                    'trash_level': int(trash_level)
                })
    
    return pd.DataFrame(data)

def plot_sensor_data(df):
    """Create multiple Seaborn plots to visualize sensor data patterns"""
    
    # Set style
    sns.set(style="whitegrid", palette="husl")
    plt.figure(figsize=(15, 20))
    
    # 1. Time Series Plot for All Sensors
    plt.subplot(4, 1, 1)
    for sensor in df['sensor_id'].unique():
        sensor_data = df[df['sensor_id'] == sensor]
        sns.lineplot(data=sensor_data, x='timestamp', y='trash_level', label=f'Sensor {sensor}', alpha=0.7)
    plt.title('Trash Level Time Series for All Sensors')
    plt.xlabel('Date')
    plt.ylabel('Trash Level (%)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # 2. Daily Patterns (Averaged)
    plt.subplot(4, 1, 2)
    df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute/60
    sns.lineplot(data=df, x='hour', y='trash_level', hue='sensor_id', 
                 estimator='mean', errorbar=None)
    plt.title('Average Daily Trash Level Patterns')
    plt.xlabel('Hour of Day')
    plt.ylabel('Average Trash Level (%)')
    plt.xticks(range(0, 24, 2))
    
    # 3. Weekly Patterns
    plt.subplot(4, 1, 3)
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    sns.boxplot(data=df, x='day_of_week', y='trash_level', hue='sensor_id')
    plt.title('Weekly Trash Level Distribution')
    plt.xlabel('Day of Week (0=Monday)')
    plt.ylabel('Trash Level (%)')
    plt.xticks(range(7), ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    
    # 4. Monthly Patterns
    plt.subplot(4, 1, 4)
    df['month'] = df['timestamp'].dt.month
    sns.boxplot(data=df, x='month', y='trash_level', hue='sensor_id')
    plt.title('Monthly Trash Level Distribution')
    plt.xlabel('Month')
    plt.ylabel('Trash Level (%)')
    
    plt.tight_layout()
    plt.show()

    # Additional Plots
    # 5. Heatmap of Daily Patterns
    plt.figure(figsize=(15, 8))
    pivot_table = df.pivot_table(index='hour', columns='sensor_id', values='trash_level', aggfunc='mean')
    sns.heatmap(pivot_table, cmap='YlOrRd', annot=False)
    plt.title('Heatmap of Average Trash Levels by Hour and Sensor')
    plt.xlabel('Sensor ID')
    plt.ylabel('Hour of Day')
    plt.show()

    # 6. Outlier Detection
    plt.figure(figsize=(15, 6))
    sns.scatterplot(data=df, x='timestamp', y='trash_level', hue='sensor_id', alpha=0.6)
    plt.title('Trash Level Measurements with Potential Outliers')
    plt.xlabel('Date')
    plt.ylabel('Trash Level (%)')
    plt.show()

if __name__ == "__main__":
    # Path to your SQL file
    sql_file = "controlled_insert.sql"
    
    # Convert SQL to DataFrame
    df = sql_to_dataframe(sql_file)
    
    # Plot the data
    plot_sensor_data(df)
    
    # Optional: Save the DataFrame for further analysis
    df.to_csv('sensor_data.csv', index=False)
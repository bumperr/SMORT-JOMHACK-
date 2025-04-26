import random
from datetime import datetime, timedelta

def generate_realistic_fake_data(sensor_id, start_time, end_time, location_factor=1.0):
    """
    Generates realistic trash level data for a sensor between start_time and end_time.
    """
    sql_statements = []
    current_time = start_time
    trash_level = 20 + int(location_factor * 10)  # Base trash level
    
    # Decide increment ranges based on sensor type
    if sensor_id in [3, 5, 6]:
        increment_range_morning = (6, 10)
        increment_range_afternoon = (20, 50)
    elif sensor_id in [1, 2, 4]:
        increment_range_morning = (0.02, 0.07)
        increment_range_afternoon = (0.05, 2)
    else:
        increment_range_morning = (0, 0.5)
        increment_range_afternoon = (1, 3)

    while current_time <= end_time:
        # Trash collection at 8 AM
        if current_time.hour == 8:
            trash_level = 0

        # Define morning (0–11) vs afternoon (12–23)
        if 0 <= current_time.hour < 12:
            increment = random.uniform(*increment_range_morning)
        else:
            increment = random.uniform(*increment_range_afternoon)

        trash_level += increment
        trash_level = min(trash_level, 100)  # Max at 100% trash level

        sql = f"INSERT INTO sensor_record (smort_ID, time_stamp, trash_level, image) VALUES ('{sensor_id}', '{current_time.strftime('%Y-%m-%d %H:%M:%S')}', {trash_level:.2f}, '');"
        sql_statements.append(sql)

        # Increase time (e.g., every hour)
        current_time += timedelta(hours=1)

    return sql_statements


if __name__ == "__main__":
    start_time = datetime(2024, 4, 26, 0, 0, 0)
    end_time = datetime(2025, 4, 26, 22, 45, 0)
    
    with open("controlled_insert.sql", "w") as file:
        for sensor_id in range(1, 10):
            location_factor = random.uniform(0.5, 1.5)
            sql_data = generate_realistic_fake_data(sensor_id, start_time, end_time, location_factor)
            for sql in sql_data:
                file.write(sql + "\n")

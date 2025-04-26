import random
from datetime import datetime, timedelta

def generate_realistic_fake_data(sensor_id, start_time, end_time, location_factor=1.0):
    sql_statements = []
    current_time = start_time
    trash_level = 20 + int(location_factor * 10)

    if sensor_id in [3, 5, 6]:
        increment_range_morning = (6, 10)
        increment_range_afternoon = (20, 50)
    elif sensor_id in [1, 2, 4]:
        increment_range_morning = (0.1, 0.4)
        increment_range_afternoon = (5, 10)
    else:
        increment_range_morning = (0, 0.5)
        increment_range_afternoon = (1, 3)

    waiting_for_reset = False
    reset_counter = 0

    while current_time <= end_time:
        if trash_level >= 100 and not waiting_for_reset:
            # Once full, start waiting
            waiting_for_reset = True
            reset_counter = random.randint(1, 3)  # Randomly wait 1-3 time steps

        if waiting_for_reset:
            reset_counter -= 1
            if reset_counter <= 0:
                trash_level = 0
                waiting_for_reset = False

        if 0 <= current_time.hour < 12:
            increment = random.uniform(*increment_range_morning)
        else:
            increment = random.uniform(*increment_range_afternoon)

        # Only increase if not full or waiting
        if not waiting_for_reset:
            trash_level += increment
            trash_level = min(trash_level, 100)

        sql = f"INSERT INTO sensor_record (smort_ID, time_stamp, trash_level, image) VALUES ('{sensor_id}', '{current_time.strftime('%Y-%m-%d %H:%M:%S')}', {trash_level:.2f}, '');"
        sql_statements.append(sql)

        current_time += timedelta(hours=1)

    return sql_statements


if __name__ == "__main__":
    start_time = datetime(2025, 2, 2, 0, 0, 0)
    end_time = datetime(2025, 4, 26, 22, 45, 0)
    
    with open("controlled_insert.sql", "w") as file:
        for sensor_id in range(1, 10):
            location_factor = random.uniform(0.5, 1.5)
            sql_data = generate_realistic_fake_data(sensor_id, start_time, end_time, location_factor)
            for sql in sql_data:
                file.write(sql + "\n")

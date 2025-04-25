import random
from datetime import datetime, timedelta

def generate_fake_trash_data(sensor_id, start_time, end_time):
    sql_statements = []
    current_time = start_time
    trash_level = 0  
    last_valid_level = trash_level  

    while current_time <= end_time:
        
        if isinstance(trash_level, int) and trash_level < 100:
            trash_level += random.randint(5, 20)

        if random.random() < 0.1 and isinstance(trash_level, int):
            trash_level = max(0, trash_level - random.randint(10, 30))  # Sudden drop
        elif random.random() < 0.05:
            trash_level = 'NULL'  
        
        if trash_level == 'NULL':
            sql_value = 'NULL'
            trash_level = last_valid_level  
        else:
            sql_value = trash_level
            last_valid_level = trash_level  
        
       
        if isinstance(trash_level, int) and trash_level >= 100:
            trash_level = 0
            last_valid_level = 0  
            sql_value = 100  
        
        
        sql = f"INSERT INTO sensor_record (smort_ID, time_stamp, trash_level, image) VALUES ('{sensor_id}', '{current_time}', {sql_value}, '');"
        sql_statements.append(sql)

        
        current_time += timedelta(minutes=15)

    return sql_statements

if __name__ == "__main__":
    start_time = datetime(2024, 2, 14, 7, 0, 0)
    end_time = start_time + timedelta(days=7)

    with open("insert.sql", "w") as file:
        for sensor_id in range(1, 10):
            sql_data = generate_fake_trash_data(sensor_id, start_time, end_time)
            for sql in sql_data:
                file.write(sql + "\n")
import requests
import random
from datetime import datetime, timedelta


#URL of your Flask application
url = 'http://127.0.0.1:5000/add_data'

#function to generate random JSON files
def generate_json_file():
    equipmentId = f'EQ-{random.randint(10000, 99999)}'
    
    #generate a random timestamp between now and one month ago
    end_time = datetime.now()
    start_time = end_time - timedelta(days=30)
    
    random_timestamp = start_time + (end_time - start_time) * random.random()
    timestamp = random_timestamp.strftime("%Y-%m-%dT%H:%M:%S%z")
    
    #defining a probability to generate None value
    if random.random() < 0.1:  # 5% chance
        value = None
    else:
        value = round(random.uniform(0.0, 200.0), 2)  # Random float between 0 and 200
    
    data = {
        'equipmentId': equipmentId,
        'timestamp': timestamp,
        'value': value
    }
    
    return data

# Send 2000 JSON files to the Flask application
def send_data_to_flask():
    for _ in range(2000):
        data = generate_json_file()
        
        response = requests.post(url, json=data)
        
        if response.status_code == 201:
            print(f"Data {data} added successfully.")
        else:
            print(f"Failed to add data {data}.")
        

if __name__ == '__main__':
    send_data_to_flask()

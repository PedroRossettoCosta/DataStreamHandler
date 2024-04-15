import random
from datetime import datetime
import time
import json
import app

# URL of your Flask application
url = 'http://127.0.0.1:5000/add_data'

def generate_json_file():

    data = {
        'equipmentId' : f'EQ-{random.randint(10000,99999)}'
        


    }
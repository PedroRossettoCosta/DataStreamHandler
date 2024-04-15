from flask import Flask, jsonify, request, render_template, session
from database import db, DataSensor
from datetime import datetime
import pandas as pd
import webbrowser
import os
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:pC1596321471307!@localhost/dbDataStreamHandler'
db.init_app(app)

@app.route('/', methods=['GET','POST'])
def home_screen():
    return render_template('home.html')


@app.route('/add_data', methods=['GET','POST'])
def add_data():
    # Extracts the JSON data from the request body using Flask
    data = request.json
    # These next lines extract specific data fields from the JSON data received in the request
    equipmentId = data['equipmentId']
    timestamp = data['timestamp']
    timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%f%z")

     #fazer tratamento para poder receber valor nulo
    if 'value' in data and data['value'] is not None:
        #If it exists, convert it to float
        value = float(data['value'])
    else:
        # If it doesn't exist or is null, set value to None
        value = None

    # Creates a new datasensor object with the extracted data and adds it to the dabase session
    new_data = DataSensor(equipmentId=equipmentId, timestamp=timestamp, value=value)
    db.session.add(new_data)
    # Commits the changes to the database
    db.session.commit()
    # This line returns a JSON response with a success message indicating that the data was added
    # successfully to the database
    return jsonify({'message': 'Data added successfully'}), 201 # Responds with 201 status code (Created) to indicate successful creation of a new resource


@app.route('/add_csv_data', methods=['GET', 'POST'])
def add_csv_data():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and file.filename.endswith('.csv'):
            
            csv_data = pd.read_csv(file, sep=',', skipinitialspace=True)

            updated_records = update_database_from_csv(csv_data)
            
            return jsonify({'message': 'CSV data processed successfully', 'updated_records': updated_records}), 200
        else:
            return jsonify({'error': 'Invalid file format, only CSV files are accepted'}), 400

    elif request.method == 'GET':
        return render_template('upload_csv.html')

def update_database_from_csv(csv_data):

    print("Processing CSV Data:")
    print(csv_data)

   # Query the database for records with matching equipmentId and null value
    records = DataSensor.query.filter(DataSensor.value.is_(None)).all()
   
    null_ids = {(record.equipmentId):record for record in records}
    
    print("records:")
    print(records)

    print("equipment:")
    print(null_ids)

    print()

    for _, row in csv_data.iterrows():
        equipmentId = row['equipmentId']
        value = float(row['value'])

        print(f"Processing equipmentId: {equipmentId}, value: {value}")

        if equipmentId in null_ids:
            record = null_ids[(equipmentId)]
            print(f"Updating record with equipmentId: {equipmentId} to value: {value}")
            record.value = value
        else:
            print(f"No matching record found for equipmentId: {equipmentId}")

    db.session.commit()
    
    return "foi caralho porra de merda de trabalho filho da puta sem mae fudido"

    


@app.route('/find_null_values', methods=['GET'])
def find_null_values():
        # Query the database for records where the 'value' field is null
    null_value_records = DataSensor.query.filter(DataSensor.value.is_(None)).all()

    null_value_records_dict = [
        {
            'id': record.id,
            'equipmentId': record.equipmentId,
            'timestamp': record.timestamp.isoformat(),  # Convert timestamp to ISO format string
            'value': record.value  # Leave value as None if it's null
        }
        for record in null_value_records
    ]
    
    # Print the null values to the terminal
    return render_template('null_values.html', null_values=null_value_records_dict)

@app.route('/graficos', methods=['GET','POST'])
def graficos():
    pass



if __name__ == '__main__':
     #Iniciando o servidor
    if not os.environ.get("WERKZEUG_RUN_MAIN"): #Executa apenas uma vez
        webbrowser.open("http://127.0.0.1:5000/")

    app.run(debug=True)
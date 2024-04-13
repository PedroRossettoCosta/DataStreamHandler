from flask import Flask, jsonify, request, render_template
from database import db, DataSensor
from datetime import datetime
import pandas as pd
import webbrowser
import os

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
        # Verifying if a file has been added
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and file.filename.endswith('.csv'):
            csv_data = pd.read_csv(file)
            # Process the CSV data as needed
            # For example, perform analysis or manipulation
            response_data = {
            'message' : 'CSV data processed successfully',
            'data' : csv_data.to_dict(orient='records') # Converts DataFrame to dictionary for JSON response
        }
            

            return jsonify(response_data), 200
        else:
            return jsonify({'error': 'Invalid file format, only CSV files are accepted'}), 400

    elif request.method == 'GET':
        return render_template('upload_csv.html')
    


@app.route('/find_null_values', methods=['GET'])
def find_null_values():
    if request.method == 'POST':
        data = request.json
        updated_records = compare_and_update_values(data)

        # Print the updated records to the terminal
        print(updated_records)

        return jsonify({'message': 'Null values updated successfully', 'updated_records': updated_records}), 200
    else:
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

@app.route('/compare_and_update_values', methods=['GET','POST'])
def compare_and_update_values(data):
    # Query the database for records where the 'value' field is null
    null_value_records = DataSensor.query.filter(DataSensor.value.is_(None)).all()

    # Create a dictionary to map record IDs to their values
    null_value_map = {record.id: record.value for record in null_value_records}

    # List to hold updated records
    updated_records = []

    # Iterate through the client's data
    for item in data:
        record_id = item['id']

        # Check if the record ID is in the null_value_map
        if record_id in null_value_map:
            # Update the value in the database
            updated_record = DataSensor.query.get(record_id)
            updated_record.value = item['value']
            db.session.commit()

            # Update the record in the null_value_map
            null_value_map[record_id] = item['value']

            # Append the updated record to the list
            updated_records.append({
                'id': record_id,
                'equipmentId': updated_record.equipmentId,
                'timestamp': updated_record.timestamp.isoformat(),
                'value': item['value']
            })

    return updated_records

if __name__ == '__main__':
     #Iniciando o servidor
    if not os.environ.get("WERKZEUG_RUN_MAIN"): #Executa apenas uma vez
        webbrowser.open("http://127.0.0.1:5000/")

    app.run(debug=True)
from flask import Flask, jsonify, request, render_template
from database import db, DataSensor
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:pC1596321471307!@localhost/dbDataStreamHandler'
db.init_app(app)



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
            
            find_null_values()
            

            return jsonify(response_data), 200
        else:
            return jsonify({'error': 'Invalid file format, only CSV files are accepted'}), 400

    elif request.method == 'GET':
        return render_template('upload_csv.html')
    
    return find_null_values()


def find_null_values():
    # Query the database for records where the 'value' field is null
    null_value_records = DataSensor.query.filter(DataSensor.value.is_(None)).all()
    
    # Convert the records to a list of dictionaries for JSON response
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
    print(null_value_records_dict)
    
    # Return a status code indicating success
    return jsonify({'message': 'Null values retrieved successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)
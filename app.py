from flask import Flask, jsonify, request, render_template
from database import db, DataSensor
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:pC1596321471307!@localhost/dbDataStreamHandler'
db.init_app(app)



@app.route('/add_data', methods=['POST'])
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


if __name__ == '__main__':
    app.run(debug=True)
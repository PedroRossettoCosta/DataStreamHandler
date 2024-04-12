from flask import Flask, jsonify, request
from database import db, DataSensor
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:pC1596321471307!@localhost/datastreamhandler'
db.init_app(app)

@app.route('/add_data', methods=['POST'])
def add_data():
    # Extract data from the request
    data = request.json
    equipmentId = data['equipmentId']
    timestamp = data['timestamp']
    timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%f%z")
    value = data['value']

    # Create a new DataSensor object and add it to the database
    new_data = DataSensor(equipmentId=equipmentId, timestamp=timestamp, value=value)
    db.session.add(new_data)
    db.session.commit()

    return jsonify({'message': 'Data added successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)
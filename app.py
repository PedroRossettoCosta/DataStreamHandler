from flask import Flask, jsonify, request, render_template
from database import db, DataSensor
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:pC1596321471307!@localhost/dbDataStreamHandler'
db.init_app(app)



@app.route('/add_data', methods=['POST'])
def add_data():
    # Extract data from the request
    data = request.json
    equipmentId = data['equipmentId']
    timestamp = data['timestamp']
    timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%f%z")
    value = float(data['value'])

    # Create a new DataSensor object and add it to the database
    new_data = DataSensor(equipmentId=equipmentId, timestamp=timestamp, value=value)
    db.session.add(new_data)
    db.session.commit()

    return jsonify({'message': 'Data added successfully'}), 201

@app.route('/add_csv_data', methods=['POST'])
def add_csv_data():
    if request.method == 'POST':
        # Verificar se o arquivo CSV foi enviado na requisição
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']

        # Verificar se o arquivo tem um nome e uma extensão válidos
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and file.filename.endswith('.csv'):
            # Ler o arquivo CSV utilizando o Pandas
            csv_data = pd.read_csv(file)
            
            # Iterar sobre as linhas do DataFrame e adicionar os dados ao banco de dados
            for index, row in csv_data.iterrows():
                equipmentId = row['equipmentId']
                timestamp = datetime.strptime(row['timestamp'], "%Y-%m-%dT%H:%M:%S.%f%z")
                value = float(row['value'])

                new_faulty_data = FaultySensorData(equipmentId=equipmentId, timestamp=timestamp, value=value)
                db.session.add(new_faulty_data)
                db.session.commit()

            return jsonify({'message': 'CSV data added successfully'}), 201
        else:
            return jsonify({'error': 'Invalid file format, only CSV files are accepted'}), 400

    elif request.method == 'GET':
        # Renderizar o formulário HTML para enviar o arquivo CSV
        return render_template('upload_csv.html')


if __name__ == '__main__':
    app.run(debug=True)
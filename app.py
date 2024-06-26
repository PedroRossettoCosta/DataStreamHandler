from flask import Flask, jsonify, request, render_template, redirect
from database import db, DataSensor
from datetime import datetime, timedelta
import pandas as pd
import webbrowser
import os
import plotly.graph_objs as go
import subprocess

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://adm_radix:radix@localhost/dbDataStreamHandler'
db.init_app(app)

#renders the home page to display the options
@app.route('/', methods=['GET','POST'])
def home_screen():
    return render_template('home.html')

#renders when the update with the CSV file is successful
@app.route('/update_success')
def update_success():
    return render_template('update_success.html')

#adds JSON data to the database
@app.route('/add_data', methods=['GET','POST'])
def add_data():
    # Extracts the JSON data from the request body using Flask
    data = request.json
    # These lines extract specific data fields from the JSON data received in the request
    equipmentId = data['equipmentId']
    timestamp = data['timestamp']
    timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S")


     #if statement for the database to accept receiving null values
    if 'value' in data and data['value'] is not None:
        #If it is not None, convert it to float
        value = float(data['value'])
    else:
        # If it doesn't exist or is null, set value to None
        value = None

    # Creates a new datasensor object with the extracted data and adds it to the dabase session
    new_data = DataSensor(equipmentId=equipmentId, timestamp=timestamp, value=value)
    #adds the new data to the session
    db.session.add(new_data)
    # Commits the changes to the database
    db.session.commit()
    # This line returns a JSON response with a success message indicating that the data was added
    # successfully to the database
    return jsonify({'message': 'Data added successfully'}), 201 # Responds with 201 status code (Created) to indicate successful creation of a new resource

#verifies the csv file added and run the update database file to send to the database the correct
#value
@app.route('/add_csv_data', methods=['GET', 'POST'])
def add_csv_data():
    if request.method == 'POST':
        #verifies if a file is added
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        #verifies if the file added has a name
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        #verifies if the file is indeed a csv file
        if file and file.filename.endswith('.csv'):
            #utilizes pandas to read the csv file and makes the result of that reading = to csv_data
            csv_data = pd.read_csv(file, sep=',', skipinitialspace=True)

            #uses the update database function to go into the database and change the correct values
            update_database_from_csv(csv_data)
            
            return redirect('/update_success')
        else:
            return jsonify({'error': 'Invalid file format, only CSV files are accepted'}), 400

    elif request.method == 'GET':
        return render_template('upload_csv.html')

# A support function for the add_csv_data that does the updating of the database
def update_database_from_csv(csv_data):

   # Query the database for records with matching equipmentId and null value
    records = DataSensor.query.filter(DataSensor.value.is_(None)).all()
   #creates a dictionary with equipmentId as the keys along the record
    null_ids = {(record.equipmentId):record for record in records}

    #iterates over the csv_data and assigns the data to the variables
    for _, row in csv_data.iterrows():
        equipmentId = row['equipmentId']
        value = float(row['value'])

        #if the variable is in the null_ids dictionary, it will updated the value 
        #that was initially null
        if equipmentId in null_ids:
            record = null_ids[(equipmentId)]
            record.value = value
        else:
            print(f"No matching record found for equipmentId: {equipmentId}")
    #commits the updated data to the database
    db.session.commit()
    
    return "The database has been successfully updated using the CSV file"

#finding the null values in the database
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
    
    
    return render_template('null_values.html', null_values=null_value_records_dict)

#renders the page where you choose what time frame average you want
@app.route('/graphs', methods=['GET','POST'])
def graphs():
    return render_template('graphs.html')

#mean calculation to find out the average values in the database for the time range specified
def get_average_values_by_time_range(time_range):
    end_time = datetime.now()
    if time_range == '24hours':
        start_time = end_time - timedelta(hours=24)
    elif time_range == '48hours':
        start_time = end_time - timedelta(hours=48)
    elif time_range == '1week':
        start_time = end_time - timedelta(weeks=1)
    elif time_range == '1month':
        start_time = end_time - timedelta(weeks=4)

   # Query the database for records within the specified time range
    records = DataSensor.query.filter(DataSensor.timestamp >= start_time, DataSensor.timestamp <= end_time).all()

    # Calculate average values
    average_values = {}
    for record in records:
        timestamp_str = record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        if timestamp_str not in average_values:
            average_values[timestamp_str] = [record.value]
        else:
            average_values[timestamp_str].append(record.value)

    #excludes None values from the lists
    average_values = {k: [v for v in vs if v is not None] for k, vs in average_values.items()}

    #calculates the average for each timestamp
    average_values = {k: sum(v) / len(v) if v else None for k, v in average_values.items()}

    #removes None values from the dictionary
    average_values = {k: v for k, v in average_values.items() if v is not None}

    #converts to DataFrame for plotting
    df = pd.DataFrame(list(average_values.items()), columns=['Timestamp', 'AverageValue'])
    
    # Calculate overall average
    overall_average = round(df['AverageValue'].mean(), 2)

    return df, overall_average

#using plotly to make the graph
@app.route('/graphs/<time_range>', methods=['GET'])
def show_graph(time_range):
    df, overall_average = get_average_values_by_time_range(time_range)
    
    # Aggregate average values by timestamp
    aggregated_df = df.groupby('Timestamp')['AverageValue'].sum().reset_index()
    
    # Create bar chart
    fig = go.Figure(data=[go.Bar(x=aggregated_df['Timestamp'], y=aggregated_df['AverageValue'],marker=dict(color='yellow',line=dict(color='blue',width=2)))])
    
    fig.update_layout(
        title=f'Total Values for {time_range.capitalize()}',
        xaxis_title='Timestamp',
        yaxis_title='Total Value',
        bargap=0.1,
        bargroupgap=0.1,
        plot_bgcolor ='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    graph_html = fig.to_html(full_html=False)

    return render_template('graph.html', graph=graph_html, overall_average=overall_average)



if __name__ == '__main__':
    #runs the computer simulator when this file is runned
    subprocess.Popen(['python','computer_simulator.py'])
     #Starting the server
    if not os.environ.get("WERKZEUG_RUN_MAIN"): #only executes one time
        webbrowser.open("http://127.0.0.1:5000/")

    app.run(debug=False)
import matplotlib.pyplot as plt
import csv
import seaborn
import base64
import js
from datetime import datetime
from io import BytesIO
from pyscript import document

def generate_graph(event):
    # Gather data from html input form
    
    # Check if date input is valid
    try:
        start_date = datetime.strptime(document.querySelector("#date_select_start").value, "%Y-%m-%d")
        timestamp_start_date = datetime.timestamp(start_date) * 1000

        end_date = datetime.strptime(document.querySelector("#date_select_end").value, "%Y-%m-%d")
        timestamp_end_date = datetime.timestamp(end_date) * 1000
    except: 
        js.alert("Invalid date range. Please select dates between 25/12/21 and 06/01/24.")
        return False
    
    if timestamp_start_date >= timestamp_end_date:
        js.alert("Start date is after end date. Please select valid date range.")
        return False
    
    timeframe = document.querySelector("#hours_select").value

    data_type = document.querySelector("#data_select").value

    # Assign dataset based on choice in form
    if data_type == "Heartrate":
        dataset = "heartrate_dataset.csv"
    elif data_type == "Stress":
        dataset = "stress_dataset.csv"
    elif data_type == "Blood Oxygen":
        dataset = "blood_oxygen_dataset.csv"

    # Dataset can't load locally so it's fetched online as outlined in pyscript.toml
    with open(dataset) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        print(csv_reader.line_num)
        loaded_dataset = {}

        # Converts dataset into float
        for i in csv_reader:
            loaded_dataset[i[0]] = i[1]

        first_key = next(iter(loaded_dataset))
        loaded_dataset.pop(first_key)

        for i in loaded_dataset:
            loaded_dataset[i] = float(loaded_dataset[i])


        # Define variables for checking time of day
        starting_date = 1640476800000
        day_length = 86400000
        night_length = 28800000

        data_points = []

        # Compile list of datapoints recorded during specified time
        for i in loaded_dataset:
            timestamp = int(i)
            current_day = (timestamp - starting_date) // day_length
            current_day_start = starting_date + (current_day * day_length)
            if (timestamp_start_date <= timestamp) and ((timestamp_end_date + day_length) >= timestamp):
                if timeframe == "Nighttime":
                    if (current_day_start <= timestamp) and ((current_day_start + night_length) >= timestamp):
                        data_points.append(loaded_dataset[i])
                elif timeframe == "Daytime":
                    if ((current_day_start + night_length) <= timestamp) and ((current_day_start + day_length) >= timestamp):
                        data_points.append(loaded_dataset[i])
                elif timeframe == "Whole Day":
                        data_points.append(loaded_dataset[i])


        # Generates a graph from the data
        seaborn.set_theme(rc={"figure.figsize": (8, 4)})
        graph = seaborn.displot(data_points, kde=True)
        plt.ylabel("Frequency")
        plt.title(data_type + " " + timeframe)

        # Crate BytesIO object and save graph before converting to base64 string
        image_stream = BytesIO()
        graph.savefig(image_stream, format='png')
        image_stream.seek(0)
        image_data = base64.b64encode(image_stream.read()).decode('utf-8')

        # Display image from base64 string
        img_output = document.querySelector("#img_output")
        img_output.src = "data:image/png;base64," + image_data


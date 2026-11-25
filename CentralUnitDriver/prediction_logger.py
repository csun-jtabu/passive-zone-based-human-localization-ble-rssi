import csv
import os
from config import OUTPUT_FOLDER
from calibration import create_pair_name

def setup_prediction_logger(experiment_name):

    # creates output directory if it doesn't exist
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # we name the csv file we are logging the data into
    file_name = f"{OUTPUT_FOLDER}/{experiment_name}_predictions.csv"

    # we create, and open the csv file in write mode
    csv_file = open(file_name, mode='w', newline='')

    # we define the headers/columns of the CSV file
    field_names = [
        "timestamp",
        "relative_time",
        "prediction",
        "truth",
        "run",
        "primary_receiver_name",
        "primary_transmitter_name",
        "pair"
    ]

    # we setup the object that will write to the csv file and the columns we write to
    csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)

    # we create the header for the csv file
    csv_writer.writeheader()

    return csv_file, csv_writer
pass

def log_prediction(csv_file, csv_writer, data, prediction):


    # we create the name of the link
    link_name = create_pair_name(data)

    # we store the data in a dictionary
    prediction_data = {
        "timestamp": data["timestamp"],
        "relative_time": data["relative_time"],
        "prediction": prediction,
        "truth": "",
        "run": "",
        "primary_receiver_name": data["receiver_name"],
        "primary_transmitter_name": data["transmitter_name"],
        "pair": link_name
    }

    csv_writer.writerow(prediction_data)  # writes dict to row
    csv_file.flush()  # forces to write to file as soon as possible

    return prediction_data
pass
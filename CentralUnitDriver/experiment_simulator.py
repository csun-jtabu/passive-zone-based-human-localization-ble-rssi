import csv
from datetime import datetime
from config import EXPERIMENT_NAME, DATA_FILE, WINDOW_SIZE
from calibration import Calibrator
from localization import Localizer
from prediction_logger import setup_prediction_logger, log_prediction
import keyboard
from preprocessing import RunningAverageFilter

def simulate():
    # this is an instance of Calibrator which is responsible for setting up the system's thresholds for all links
    calibrator = Calibrator()

    # this variable will store a dict containing our baseline thresholds for each link
    fingerprint = None

    # this is an instance of Localizer which is responsible for predicting where human presence is
    localizer = Localizer()

    # this creates the csv file and csv writer for logging predictions
    csv_predictions, csv_prediction_writer = setup_prediction_logger(EXPERIMENT_NAME)

    # this creates an instance of running average filter with a specified window size
    rssi_filter = RunningAverageFilter(window_size=WINDOW_SIZE)

    try:
        # we open the file pertaining to the chosen experiment scenario
        with open(DATA_FILE, mode='r', newline="") as csv_file:

            # we pass the file into the reader
            csv_reader = csv.DictReader(csv_file)

            # we go through each row in the csv file collected by the data recorder
            for row in csv_reader:

                # we stop predicting if q is pressed on keyboard at anytime
                if keyboard.is_pressed('q'):
                    print("Stopping simulator")
                    break

                # puts each row in the form of a dictionary
                data = {
                    "timestamp": row["timestamp"],
                    "relative_time": int(row["relative_time"]),
                    "receiver_name": row["receiver_name"],
                    "transmitter_name": row["transmitter_name"],
                    "rssi": int(row["rssi"])
                }

                # runs the data received into the filter
                data["rssi"] = rssi_filter.filter(
                    data["receiver_name"],
                    data["transmitter_name"],
                    data["rssi"]
                )

                # this is the current measurement's time since the first entry of the entire recording
                elapsed_time = data["relative_time"]

                # if a fingerprint of the environment doesn't exist yet, then try to generate one
                if fingerprint is None:
                    # this passes the data and elapsed time to calibrate the system's thresholds
                    fingerprint = calibrator.calibrate_system(data, elapsed_time)
                else: # if a fingerprint of the environment already exists
                    # make a prediction on the data by using the fingerprint
                    prediction, primary_link = localizer.predict_quadrant(data, fingerprint)

                    # if a prediction is made, then we print the output on the console and save it in the predictions log
                    if prediction is not None:
                        print(prediction)
                        log_prediction(csv_predictions, csv_prediction_writer, primary_link, prediction)

    except KeyboardInterrupt:
        print("Stopping predictions and data feeding")
    finally:
        csv_predictions.close()

if __name__ == "__main__":
    simulate()
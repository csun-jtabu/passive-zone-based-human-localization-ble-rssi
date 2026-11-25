from datetime import datetime
from data_recorder import setup_connection, setup_csv, receive_data, format_and_save_data
from config import EXPERIMENT_NAME
from calibration import Calibrator
from localization import Localizer
from prediction_logger import setup_prediction_logger, log_prediction
import keyboard

def main():
    # this is the start time of the program recording
    experiment_start_time = datetime.now()

    # we set up the sock connection in which we listen to broadcasts via WiFi from the anchors
    sock = setup_connection()

    # this creates the actual csv file and csv writer
    csv_file, csv_writer = setup_csv(EXPERIMENT_NAME)

    # this is an instance of Calibrator which is responsible for setting up the system's thresholds for all links
    calibrator = Calibrator()

    # this variable will store a dict containing our baseline thresholds for each link
    fingerprint = None

    # this is an instance of Localizer which is responsible for predicting where human presence is
    localizer = Localizer()

    # this creates the csv file and csv writer for logging predictions
    csv_predictions, csv_prediction_writer = setup_prediction_logger(EXPERIMENT_NAME)

    try:
        while True:
            # we stop recording once q is pressed on keyboard
            if keyboard.is_pressed('q'):
                print("Stopping logger")
                break

            # we retrieve the data from the socket connection
            message_parts = receive_data(sock)

            # if we don't receive data or if the data is invalid, then we restart
            if message_parts is None:
                continue

            # this saves the data into a CSV file and returns the entry in the form of a dictionary
            data = format_and_save_data(csv_file, csv_writer, message_parts, experiment_start_time)

            # this is the time since the start of the program
            elapsed_time = (datetime.now() - experiment_start_time).total_seconds()

            # if a fingerprint of the environment doesn't exist yet, then try to generate one
            if fingerprint is None:
                # this passes the data and elapsed time to calibrate the system's thresholds
                fingerprint = calibrator.calibrate_system(data, elapsed_time)
            else:  # if a fingerprint of the environment already exists
                # make a prediction on the data by using the fingerprint
                prediction, primary_link = localizer.predict_quadrant(data, fingerprint)

                # if a prediction is made, then we print the output on the console and save it in the predictions log
                if prediction is not None:
                    print(prediction)
                    log_prediction(csv_predictions, csv_prediction_writer, primary_link, prediction)

    except KeyboardInterrupt:
        print("Stopping listener")
    finally:
        sock.close()
        csv_file.close()
        csv_predictions.close()

if __name__ == "__main__":
    main()
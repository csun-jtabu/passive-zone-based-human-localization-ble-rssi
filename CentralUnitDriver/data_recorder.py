from datetime import datetime
from config import UDP_IP, UDP_PORT, OUTPUT_FOLDER
import socket
import csv
import os

def setup_connection():
    # this will create an end point on the python side to receive data from the ESP32
    # socket.AF_INET defines what address family the program should expect - IPV4 in this case
    # socket.SOCK_DGRAM defines what socket type to use - Connectionless socket / UDP in this case
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # this makes it so that the program listens to broadcast packets
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # allows port reuse
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # this creates the actual connection/socket
    sock.bind((UDP_IP, UDP_PORT))

    # just a note to tell us that the program is listening
    print(f"Listening for UDP packets on port {UDP_PORT}...")

    # we return the sock object
    return sock
pass

def setup_csv(experiment_name):

    # creates output directory if it doesn't exist
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # we name the csv file we are logging the data into
    file_name = f"{OUTPUT_FOLDER}/{experiment_name}.csv"

    # we create, and open the csv file in write mode
    csv_file = open(file_name, mode='w', newline='')

    # we define the headers/columns of the CSV file
    field_names = [
        "timestamp",
        "relative_time",
        "receiver_name",
        "transmitter_name",
        "rssi"
    ]

    # we setup the object that will write to the csv file and the columns we write to
    csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)

    # we create the header for the csv file
    csv_writer.writeheader()

    return csv_file, csv_writer
pass

def receive_data(sock):
    data, addr = sock.recvfrom(1024)  # we save what we received and the ip address it's coming from
    message = data.decode().strip()  # removes any whitespace and decodes the data
    print(f"Received from {addr}: {message}")  # we just print out what we received in the console

    # we split the data into 3 parts
    message_parts = message.split(",")

    # makes sure the receiving data is in the following format: receiver_name, transmitter_name, rssi
    if len(message_parts) == 3:
        return message_parts
    else:
        print(f"Invalid packet received and tossed")
        return None
pass

def format_and_save_data(csv_file, csv_writer, message_parts, experiment_start_time):

    receiver_name, transmitter_name, rssi = message_parts  # saves the data into their respective variables

    current_timestamp = datetime.now()  # this timestamp is for the current entry
    relative_time = int((current_timestamp - experiment_start_time).total_seconds()+0.5)  # calculates the relative time for the current entry and rounds similar to Excel

    timestamp_str = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")  # converts the current timestamp to something more excel friendly

    rssi = int(rssi)  # converts rssi from string to int

    data = {
        "timestamp": timestamp_str,
        "relative_time": relative_time,
        "receiver_name": receiver_name,
        "transmitter_name": transmitter_name,
        "rssi": rssi
    }

    csv_writer.writerow(data)  # writes to row
    csv_file.flush()  # forces to write to file as soon as possible

    return data
pass

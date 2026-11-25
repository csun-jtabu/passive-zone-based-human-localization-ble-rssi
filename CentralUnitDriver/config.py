# UDP settings
UDP_IP = ""  # we listen to our WiFi interface
UDP_PORT = 6700  # this is the port the program will listen on

# CSV settings
OUTPUT_FOLDER = "data"

# Experiment information
EXPERIMENT_NAME = "new_movement_3"

# Setup time for calibrating the system's thresholds
CALIBRATION_TIME = 60

# This is the size of the window for running average filter
WINDOW_SIZE = 3

# Dict containing the quadrant (key) and the links that are
# primarily used to tell if there is human presence in a quadrant
# (Change this depending on deployment/anchor placement in a room)
QUADRANT_PRIMARY_LINKS = {
    "Q1": ["Anchor_2-Anchor_3"],
    "Q2": ["Anchor_1-Anchor_4"],
    "Q3": ["Anchor_2-Anchor_3"],
    "Q4": ["Anchor_1-Anchor_4"],
}

# Dict containing the quadrant (key) and the supporting links that
# help narrow localization
# (Change this depending on deployment/anchor placement in a room)
QUADRANT_SUPPORTING_LINKS= {
    "Q1": ["Anchor_1-Anchor_2", "Anchor_2-Anchor_4"],
    "Q2": ["Anchor_1-Anchor_2", "Anchor_1-Anchor_3"],
    "Q3": ["Anchor_1-Anchor_3", "Anchor_3-Anchor_4"],
    "Q4": ["Anchor_2-Anchor_4", "Anchor_3-Anchor_4"],
}

# This is how much we can deviate from the baseline
# Ex. 0 - Any rssi_change below 0 indicates the signal dropped below its baseline
# More Positive Values will make the detector MORE sensitive.
# Ex. 1 - By raising it, we allowed smaller RSSI drops to trigger detection
# More Negative Values will make the detector LESS sensitive
# Ex. -1 - By lowering it, we made it the system require a larger RSSI drop before detection
LOCALIZATION_THRESHOLD = 0

# This will be the file name we will be inputting into experiment simulator
DATA_FILE = f"data/run data log/{EXPERIMENT_NAME}.csv"

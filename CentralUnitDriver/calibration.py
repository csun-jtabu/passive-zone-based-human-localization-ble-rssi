from config import CALIBRATION_TIME
class Calibrator:

    def __init__(self):
        self.calibration_data = [] # list to store incoming data for calibration
        self.environment_fingerprint = {} # dict for containing the name of each link (key) and its avg rssi value (value)

    def calibrate_system(self, data, elapsed_time):
        # if run time is still before the calibration time limit, collect calibration data
        if elapsed_time < CALIBRATION_TIME:
            print("Collecting Data for Calibration...")
            self.calibration_data.append(data)
            return None
        else: # if calibration time limit has been reached, stop collecting, and generate the fingerprint
            print("Generating fingerprint")
            # return the fingerprint/baseline values for system based on the average
            self.create_env_fingerprint()
            return self.environment_fingerprint
    pass

    def create_env_fingerprint(self):
        # this dict contains the name of the link (key) and the list of RSSI entries that corresponds to that link (value)
        # ex: "Anchor_1-Anchor_2"
        links_data = {}

        # we look at each logged entry in the list of data we received for calibration
        # essentially, we sort the data into their corresponding links
        for entry in self.calibration_data:

            # we create a string that is in the following format: Anchor_X-Anchor_Y to insert in links_data dict
            link = create_pair_name(entry)

            # initializes a link entry in the links_data dict with an empty list if it doesn't exist already
            if link not in links_data:
                links_data[link] = []

            # we add the rssi of the current entry into link_data dict's list that corresponds with the link name (key)
            links_data[link].append(entry["rssi"])

        # for each link in our links_data dict
        for link in links_data:

            # if there is a non-empty list of rssi entries for that link
            if len(links_data[link]) > 0:
                # we calculate the average (mean) RSSI by adding all the entries in the links_data list (value)
                # and dividing it by the number of entries in links_data list
                average = sum(links_data[link]) / len(links_data[link])

                # store the average value into our environment_fingerprint dict {link:avg rssi}
                self.environment_fingerprint[link] = average
    pass
pass


# helper method for creating links in the following form: "Anchor_1-Anchor_2"
def create_pair_name(entry):
    # we create a string that is in the following format: Anchor_X-Anchor_Y to insert in links_data dict
    # we put both names in a list
    link = [entry["receiver_name"], entry["transmitter_name"]]

    # sort the list so the anchor numbers are in order and
    # to consolidate link entries in both directions into one bidirectional link
    link = sorted(link)

    # create a string that joins the two transmitter/receiver names in the list with a hyphen
    link = "-".join(link)

    return link
pass
from calibration import create_pair_name


class RunningAverageFilter:
    def __init__(self, window_size=3):
        self.window_size = window_size # this is how many numbers we want to avg for the filter
        self.windows = {} # this is the dictionary that will store the windows for each link. each links has its own window filter

    def filter(self, receiver_name, transmitter_name, rssi):
        # creates the name of the link we want to make a window for
        link = create_pair_name({
            "receiver_name": receiver_name,
            "transmitter_name": transmitter_name
        })

        # if there isn't a window made already for a link. create one by making an empty list
        if link not in self.windows:
            self.windows[link] = []

        # add the newest RSSI measurement to the window for the specific link
        self.windows[link].append(rssi)

        # if the window for a link is full, then remove the earliest value from the window
        if len(self.windows[link]) > self.window_size:
            self.windows[link].pop(0)

        # calculate the average rssi from all rssi values in a link's window
        average = sum(self.windows[link]) / len(self.windows[link])

        # return the "running_average"
        return average

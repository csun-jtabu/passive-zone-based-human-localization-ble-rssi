from config import QUADRANT_PRIMARY_LINKS, QUADRANT_SUPPORTING_LINKS, LOCALIZATION_THRESHOLD
from calibration import create_pair_name
class Localizer:

    def __init__(self):
        # we create an empty dictionary to act as a buffer for each link in the system
        # one entry is being processed at a time, but the system needs to evaluate all links to make a prediction
        # once it's full, then we make a prediction
        self.fusion_buffer = {}

        # we create a set containing every link that is used as a primary link
        # (we use a set to ensure there's no duplicate entries)
        self.primary_links = set()

        # we populate a set containing the primary links that were defined in the config file
        for links in QUADRANT_PRIMARY_LINKS.values():
            self.primary_links.update(links)

        # flag to check if prediction by fusing entries is ready
        self.prediction_ready = False
    pass

    def predict_quadrant(self, entry, fingerprint):
        # this initializes the buffer to expect the same links from the system's fingerprint
        if len(self.fusion_buffer) == 0:
            for link in fingerprint:
                self.fusion_buffer[link] = None

        # we generate the name of the link we are looking for from the entry data's receiver and transmitter fields
        link_name = create_pair_name(entry)

        # store most recent entry for this link in the fusion_buffer
        self.fusion_buffer[link_name] = entry

        # we loop through each link in the fusion buffer
        for link in self.fusion_buffer:

            # if we encounter a link that hasn't been assigned a value, we flag as not ready (False) and break the loop
            if self.fusion_buffer[link] == None:
                self.prediction_ready = False
                break
            else: # if we encounter a link that is assigned, it remains true
                self.prediction_ready = True

        # if the fusion buffer is loaded, we make a prediction based on all the entries in it
        if self.prediction_ready == True:
            print("Predicting...")
            # we make an initial prediction on the received data using the fingerprint we made for each link
            # we get the possible quadrants and the primary link that triggered the system
            candidate_quadrants, primary_link = self.check_primary_links(fingerprint)

            # we get the entry in the buffer that has the latest time
            # this is to get the timestamp and to properly represent the point in time a prediction is made/for
            latest_entry = max(self.fusion_buffer.values(), key=lambda x: x["relative_time"])

            # if a primary link is none, this means that the system wasn't triggered and there is
            # No Human Presence. We still want to log this so we generate an entry for it
            if primary_link is None:
                final_prediction = "No Presence"

                primary_link = {
                    "timestamp": latest_entry["timestamp"],
                    "relative_time": latest_entry["relative_time"],
                    "receiver_name": "",
                    "transmitter_name": "",
                    "rssi": ""
                }
            else: # else we narrow down our prediction using the secondary links
                final_prediction = self.check_supporting_links(candidate_quadrants)

                # we edit the timestamp and relative time entry to reflect the ending of the fusion window
                # rather than when primary_link was collected.
                primary_link = {
                    "timestamp": latest_entry["timestamp"],
                    "relative_time": latest_entry["relative_time"],
                    "receiver_name": primary_link["receiver_name"],
                    "transmitter_name": primary_link["transmitter_name"],
                    "rssi": primary_link["rssi"]
                }

            # we clear the buffer for the next prediction
            self.fusion_buffer = {}

            # and reset the ready flag
            self.prediction_ready = False

            # we return the final prediction and the primary link that triggered the system and, a boolean that represents the prediction
            return final_prediction, primary_link
        else:   # else, it will not make a prediction and return none
            return None, None
    pass

# helper function for comparing how different the threshold is from the current reading
    def calculate_rssi_change(self, link, incoming_rssi, fingerprint):

        # we retrieve the baseline RSSI from the fingerprint pertaining to the interested link
        baseline_rssi = fingerprint[link]

        # we see how different the incoming RSSI is against our baseline
        rssi_change = incoming_rssi - baseline_rssi

        return rssi_change
    pass

# when the buffer is fully loaded the first step to prediction is made by looking at the primary links
# this is the helper function used to find the primary triggering link which would then be used to narrow down what
# quadrants to look at
    def check_primary_links(self, fingerprint):

        # this will store the quadrants that can possibly be where human presence is
        candidate_quadrants = []

        # this will store the primary link that may have triggered the prediction
        triggering_link = None

        # for each link in the buffer
        for link_name, entry in self.fusion_buffer.items():

            # if link is listed as a primary link in the config
            if link_name in self.primary_links:

                # we calculate the change in RSSI between the current entry and the established baseline
                # ex: -10 would indicate a drop from baseline
                # ex: 10 would indicate a spike from baseline
                rssi_change = self.calculate_rssi_change(link_name, entry["rssi"], fingerprint)

                # if the change in RSSI is less than what is allowed, and...
                if rssi_change < LOCALIZATION_THRESHOLD:

                    # if a link hasn't been found or if the new possible triggering link is less than the current one
                    if (triggering_link is None) or (entry["rssi"] < self.fusion_buffer[triggering_link]["rssi"]):
                        triggering_link = link_name # then the current link will be considered as the triggering link

        # if there is a primary link that drops below threshold,
        if triggering_link is not None:

            # we look at each quadrant's listed primary link to see...
            for quadrant, links in QUADRANT_PRIMARY_LINKS.items():
                # if the link is in quadrant's list of links.
                # if it is, we add the quadrant to our list of candidate quadrants
                if triggering_link in links:
                    candidate_quadrants.append(quadrant)

            # we return the list of quadrants that might have human presence in them and the entire data entry
            # that triggered the system
            return candidate_quadrants, self.fusion_buffer[triggering_link]

        return candidate_quadrants, None
    pass

# after finding the primary triggering link, we are given the candidate quadrants to look at
# however, we still don't know the specific quadrant a human is in
# to find the single quadrant, we must look at the supporting links that cross each candidate quadrant.
# even though human presence doesn't directly cross the supporting links, preliminary findings suggested that
# human presence is highly likely to be in a candidate quadrant with a group of links with the lowest minimum rssi
    def check_supporting_links(self, candidate_quadrants):
        # this will be the name of the quadrant that we detect
        predicted_quadrant = None

        # this will hold the group minimums of each quadrant
        quadrant_scores = {}

        # this will hold the lowest rssi amongst the quadrant scores
        final_lowest_rssi = None

        # for each quadrant in our primary results, we try to find the link with the lowest RSSI in that quadrant
        for quadrant in candidate_quadrants:

            # this is the variable to hold the minimum rssi for the quadrant
            quadrant_min_rssi = None

            # we then look at each supporting link for each candidate quadrant
            for supporting_link in QUADRANT_SUPPORTING_LINKS[quadrant]:

                # if we have an entry saved pertaining to the supporting link
                if supporting_link in self.fusion_buffer:

                    #  we obtain its measured RSSI for comparison
                    current_rssi = self.fusion_buffer[supporting_link]["rssi"]

                    # if there isn't a quadrant minimum yet, or the current link's rssi beats the current minimum rssi
                    if (quadrant_min_rssi is None) or (current_rssi < quadrant_min_rssi):

                        # the current_rssi becomes the new minimum rssi
                        quadrant_min_rssi = current_rssi

            # after determining the lowest rssi among each quadrant, we save the value in quadrant scores
            quadrant_scores[quadrant] = quadrant_min_rssi


        # now we look for the smallest rssi amongst the minimum rssis from each quadrant
        for quadrant, rssi in quadrant_scores.items():

            # skips the quadrant if there wasn't an rssi recorded for the quadrant
            if rssi is None:
                continue

            # if there still isn't a minimum rssi found amongst all quadrants,
            # or if there is a quadrant with a lower rssi value
            if (final_lowest_rssi is None) or (rssi < final_lowest_rssi):

                # we save the new lowest, and the current rssi overwrites the current lowest
                final_lowest_rssi = rssi

                # this would also mean that the current quadrant will be the new predicted quadrant
                predicted_quadrant = quadrant

        return predicted_quadrant
    pass
pass


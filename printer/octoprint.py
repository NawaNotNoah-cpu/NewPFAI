import requests

from config import *


HEADERS = {
    "X-Api-Key": API_KEY
}
def safe_int(value):

    try:
        return int(value)

    except (ValueError, TypeError):
        return None

class OctoPrinter:

    def api(self, endpoint):

        response = requests.get(
            OCTOPRINT_URL + endpoint,
            headers=HEADERS,
            timeout=5
        )

        response.raise_for_status()

        return response.json()


    def printer(self):

        return self.api("/api/printer")


    def job(self):

        return self.api("/api/job")


    def layer(self):

        return self.api(
            "/plugin/DisplayLayerProgress/values"
        )


    def state(self):

        printer = self.printer()
        job = self.job()
        layer = self.layer()

        return {

            "state":
                job["state"],

            "progress":
                job["progress"]["completion"],

            "current_layer":
                safe_int(layer["layer"]["current"]),

            "total_layers":
                safe_int(layer["layer"]["total"]),

            "nozzle":
                printer["temperature"]["tool0"]["actual"],

            "bed":
                printer["temperature"]["bed"]["actual"]
        }
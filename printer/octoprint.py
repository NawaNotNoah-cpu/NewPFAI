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


def safe_get(dictionary, *keys):
    """
    Safely traverse nested dictionaries.
    Returns None if any key is missing.
    """
    current = dictionary

    for key in keys:
        if not isinstance(current, dict):
            return None

        current = current.get(key)

        if current is None:
            return None

    return current

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

    def filename(self):

        job = self.job()

        try:
            return job["job"]["file"]["name"]
        except Exception:
            return "unknown.gcode"
        def job(self):

            return self.api("/api/job")
    
    def pause(self):

        requests.post(
            OCTOPRINT_URL + "/api/job",
            headers=HEADERS,
            json={
                "command":"pause",
                "action":"pause"
            },
            timeout=5
        )

    def resume(self):

        requests.post(
            OCTOPRINT_URL + "/api/job",
            headers=HEADERS,
            json={
                "command":"pause",
                "action":"resume"
            },
            timeout=5
        )

    def cancel(self):

        requests.post(
            OCTOPRINT_URL + "/api/job",
            headers=HEADERS,
            json={
                "command":"cancel"
            },
            timeout=5
        )

    def layer(self):

        return self.api(
            "/plugin/DisplayLayerProgress/values"
        )


    def state(self):

        printer = self.printer()
        job = self.job()
        layer = self.layer()

        return {
    "z":
    float(
        safe_get(
            layer,
            "height",
            "current"
        ) or 0.0
    ),

    "state":
        job.get("state"),

    "progress":
        job.get("progress", {}).get("completion"),

    "current_layer":
        safe_int(
            safe_get(layer, "layer", "current")
        ),

    "total_layers":
        safe_int(
            safe_get(layer, "layer", "total")
        ),

    "nozzle":
        safe_get(
            printer,
            "temperature",
            "tool0",
            "actual"
        ),

    "bed":
        safe_get(
            printer,
            "temperature",
            "bed",
            "actual"
        )
}
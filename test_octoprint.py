import time
import requests


# ==========================================
# CONFIG
# ==========================================

OCTOPRINT_URL = "http://localhost:2960"

API_KEY = (
    "8AMs4cQluTyw8qk8qb0tjNBPEMbVfleJMoPYHPC2QS8"
)

HEADERS = {
    "X-Api-Key": API_KEY
}


# ==========================================
# HELPERS
# ==========================================

def api(endpoint):

    url = OCTOPRINT_URL + endpoint

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=5
    )

    response.raise_for_status()

    return response.json()


# ==========================================
# DISPLAY LAYER PROGRESS
# ==========================================

def get_layer():

    try:

        return api(
            "/plugin/DisplayLayerProgress/values"
        )

    except Exception as e:

        print("Layer plugin error:", e)

        return None


# ==========================================
# PRINTER INFO
# ==========================================

def get_printer():

    return api("/api/printer")


# ==========================================
# JOB INFO
# ==========================================

def get_job():

    return api("/api/job")


# ==========================================
# MAIN
# ==========================================

while True:

    try:

        printer = get_printer()
        job = get_job()
        layer = get_layer()
        print("\n------------------------------")

        #
        # Printer state
        #

        print(
            "State:",
            job["state"]
        )

        #
        # Progress
        #

        completion = (
            job["progress"]
            .get("completion")
        )

        if completion is None:
            completion = 0

        print(
            f"Progress: {completion:.1f}%"
        )

        #
        # Layer
        #

        if layer:

            current_layer = int(layer["layer"]["current"])
            total_layers = int(layer["layer"]["total"])

            print(f"Current Layer: {current_layer}")
            print(f"Total Layers: {total_layers}")

        #
        # Temperatures
        #

        tool = printer["temperature"]["tool0"]

        bed = printer["temperature"]["bed"]

        print(
            "Nozzle:",
            tool["actual"]
        )

        print(
            "Bed:",
            bed["actual"]
        )

    except Exception as e:

        print(e)

    time.sleep(5)
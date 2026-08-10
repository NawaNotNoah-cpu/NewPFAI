import requests
import time
from config import *


HEADERS = {
    "X-Api-Key": OCTOPRINT_API_KEY
}


def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def safe_get(dictionary, *keys):
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


    def job(self):

        return self.api("/api/job")


    def filename(self):

        try:

            job = self.job()

            filename = (
                job
                .get("job", {})
                .get("file", {})
                .get("name")
            )

            if filename:
                return filename

        except Exception as e:

            print("Filename error:", e)

        return "unknown.gcode"


    def state(self):

        printer = self.printer()
        job = self.job()
        layer = self.layer()

        return {
            "z": None,

            "state":
                job.get("state"),

            "progress":
                float(
                    job.get(
                        "progress",
                        {}
                    ).get("completion") or 0.0
                ),

            "current_layer":
                safe_int(
                    safe_get(
                        layer,
                        "layer",
                        "current"
                    )
                ),

            "total_layers":
                safe_int(
                    safe_get(
                        layer,
                        "layer",
                        "total"
                    )
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


    def layer(self):

        return self.api(
            "/plugin/DisplayLayerProgress/values"
        )


    def cancel(self):

        response = requests.post(
            OCTOPRINT_URL + "/api/job",
            headers=HEADERS,
            json={
                "command": "cancel"
            },
            timeout=5
        )

        response.raise_for_status()


    def gcode(self, command):

        response = requests.post(
            OCTOPRINT_URL + "/api/printer/command",
            headers=HEADERS,
            json={
                "commands": [command]
            },
            timeout=5
        )

        response.raise_for_status()


    def select_file(self, filename):

        response = requests.post(
            OCTOPRINT_URL
            + "/api/files/local/"
            + filename,
            headers=HEADERS,
            json={
                "command": "select",
                "print": True
            },
            timeout=5
        )

        response.raise_for_status()


    def wait_for_cooling(
        self,
        nozzle_target=150,
        bed_target=50,
        tolerance=10,
        timeout=900
    ):

        print("Waiting for printer to cool...")

        start = time.time()

        while True:

            state = self.state()

            nozzle = state["nozzle"]
            bed = state["bed"]

            print(
                f"Nozzle: {nozzle} C | "
                f"Bed: {bed} C"
            )

            nozzle_ready = (
                nozzle is not None
                and nozzle <= nozzle_target + tolerance
            )

            bed_ready = (
                bed is not None
                and bed <= bed_target + tolerance
            )

            if nozzle_ready and bed_ready:

                print("Printer cooled.")

                return True

            if time.time() - start > timeout:

                print(
                    "Cooling timeout reached."
                )

                return False

            time.sleep(5)


    def wait_for_idle(
        self,
        timeout=120
    ):

        print("Waiting for printer to become idle...")

        start = time.time()

        while True:

            state = self.state()

            printer_state = state["state"]

            print(
                "OctoPrint state:",
                printer_state
            )

            if printer_state in (
                "Operational",
                "Ready",
                "Closed"
            ):

                return True

            if time.time() - start > timeout:

                print(
                    "Printer idle timeout reached."
                )

                return False

            time.sleep(2)


    def wait_for_motion(self):

        print("Waiting for printer motion to finish...")

        # M400 causes the firmware to wait for all
        # previously queued movement to complete.
        self.gcode("M400")

        time.sleep(2)

        print("Motion complete.")


    def prepare_for_extraction(
        self,
        nozzle_target=175,
        bed_target=57,
        timeout=900,
    ):

        print("Preparing printer for extraction...")

        # Stop heating.
        self.gcode(f"M104 S{nozzle_target}")
        self.gcode(f"M140 S{bed_target}")

        # Home first.
        print("Homing printer...")
        self.gcode("G28")

        # Move to extraction position.
        print("Moving printer to extraction position...")
        self.gcode("G1 Y235 Z250 F3000")

        # IMPORTANT:
        # Wait for all queued firmware motion to finish.
        self.gcode("M400")

        # Now independently wait for the heaters to be safe.
        print("Waiting for printer to cool...")

        if not self.wait_for_cooling(
            nozzle_target=nozzle_target,
            bed_target=bed_target,
            tolerance=10,
            timeout=timeout
        ):
            return False

        print("Printer cooled.")

        # Give the printer a final moment after the firmware queue
        # has drained and temperatures have stabilized.
        time.sleep(30)

        print("Printer is safe for extraction.")

        return True

    def wait_for_operational(
        self,
        timeout=120
    ):

        print("Waiting for printer to become operational...")

        start = time.time()

        while True:

            job = self.job()
            state = job.get("state")

            print("OctoPrint state:", state)

            if state in (
                "Operational",
                "Ready"
            ):
                print("Printer is operational.")
                return True

            if time.time() - start > timeout:

                print("Printer operational timeout.")

                return False

            time.sleep(2)


    def start_print(self, filename):

        print(
            f"Starting new print: {filename}"
        )

        self.select_file(filename)

        start = time.time()
        timeout = 30

        while True:

            job = self.job()

            state = job.get("state")

            selected = (
                job.get("job", {})
                .get("file", {})
                .get("name")
            )

            print(
                f"OctoPrint state: {state} | "
                f"File: {selected}"
            )

            if (
                selected == filename
                and state in (
                    "Printing",
                    "Preparing"
                )
            ):
                print("New print confirmed.")
                return True

            if time.time() - start > timeout:

                print(
                    "Timed out waiting for new print."
                )

                return False

            time.sleep(2)
    def wait_for_print_start(
        self,
        filename,
        timeout=60
    ):

        print(
            f"Waiting for {filename} to become active..."
        )

        start = time.time()

        while True:

            job = self.job()

            state = job.get("state")

            current_file = (
                job.get("job", {})
                .get("file", {})
                .get("name")
            )

            print(
                f"State: {state} | "
                f"File: {current_file}"
            )

            if (
                current_file == filename
                and state == "Printing"
            ):
                print("Replacement print is active.")
                return True

            if time.time() - start > timeout:

                print(
                    "Timed out waiting for replacement print."
                )

                return False

            time.sleep(2)
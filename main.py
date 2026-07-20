import time

from config import *

from camera.webcam import Webcam
from printer.octoprint import OctoPrinter
from vision.qwen import QwenVision


camera = Webcam(CAMERA_INDEX)

printer = OctoPrinter()

vision = QwenVision(MODEL_NAME)

last_layer = -1

print("System Ready")


try:

    while True:

        state = printer.state()

        print()

        print(state)

        current_layer = state["current_layer"]

        #
        # New layer?
        #

        if current_layer != last_layer:

            last_layer = current_layer

            filename = (
                f"layer_{current_layer:04d}.jpg"
            )

            image = camera.capture(
                IMAGE_OUTPUT_DIR,
                filename
            )

            print(
                f"Captured {filename}"
            )

            #
            # Later this becomes:
            #
            # render layer
            # compare
            #

            result = vision.analyze(image)

            print(result)

        time.sleep(POLL_INTERVAL)

finally:

    camera.release()
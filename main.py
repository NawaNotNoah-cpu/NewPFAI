import time
from config import *

from camera.webcam import Webcam
from printer.octoprint import OctoPrinter 
from renderer.renderer import GCodeRenderer
from vision.qwen import QwenVision
from scheduler.layer_scheduler import LayerScheduler
from session import create_session
import json


camera = Webcam(CAMERA_INDEX)

printer = OctoPrinter()
renderer = GCodeRenderer(
    GCODE_FILE
)
scheduler = LayerScheduler(
    INSPECTION_INTERVALS
)

vision = QwenVision(MODEL_NAME)

last_layer = -1
scheduler_initialized = False


print("System Ready")


try:

    while True:

        state = printer.state()
        total_layers = state["total_layers"]


        if (
            not scheduler_initialized
            and total_layers is not None
        ):

            scheduler.initialize(
                total_layers
            )

            scheduler_initialized = True

        current_layer = state["current_layer"]

        if current_layer is None:

            print("Waiting for active print...")

            time.sleep(30)

            continue
        print()

        print(state)
        print(
            "Next inspection:",
            scheduler.next_target()
        )

        if scheduler.should_capture(
            current_layer
        ):

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


            print(
                f"Rendering layer {current_layer}"
            )

            renderer.render_layer(
                current_layer
            )


            print(
                "Render complete"
            )

        time.sleep(POLL_INTERVAL)

        render = f"{RENDER_OUTPUT_DIR}/layer_{current_layer:04d}.png"

        metadata = {

            "print_name": print_name,

            "attempt": attempt,

            "layer": current_layer,

            "total_layers": state["total_layers"],

            "progress": state["progress"],

            "z_height": state["z"]
        }

        result = vision.analyze(

            image,

            render,

            metadata
        )

        analysis = json.loads(result)
        print(analysis)

        if(
            not analysis["healthy"]
            and analysis["severity"] >= 7
        ):
    

            printer.pause()
            print(
                "Print paused due to detected issue."
            )


finally:

    camera.release()
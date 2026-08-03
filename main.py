import time

from networkx import config
from config import *
import os

from camera.webcam import Webcam
from printer.octoprint import OctoPrinter 
from renderer.renderer import GCodeRenderer
from vision.qwen import QwenVision
from cobot.extractor import extractor
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
filename = printer.filename()

if filename is None:
    filename = "unknown.gcode"

print_name = os.path.splitext(filename)[0]

session, attempt = create_session(print_name)

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

            basename = (
                f"{print_name}"
                f"_I{attempt:03d}"
                f"_L{current_layer:04d}"
            )

            image = camera.capture(
                session / "images",
                f"{basename}.jpg"
            )

            print(f"Captured {basename}.jpg")


            print(
                f"Rendering layer {current_layer}"
            )

            render = (
                session
                / "renders"
                / f"{basename}.png"
            )

            renderer.render_layer(
                current_layer,
                render
            )


            print(
                "Render complete"
            )

            metadata = {

                "print_name": print_name,

                "attempt": attempt,

                "layer": current_layer,

                "total_layers": state["total_layers"]
                    if state["total_layers"] is not None
                    else 0,

                "progress": state["progress"]
                    if state["progress"] is not None
                    else 0.0,

                "z_height": renderer.get_layer_height(current_layer)
                    if state["z"] is not None
                    else 0.0,

                "LINE_COLOR": config.LINE_COLOR,

                "FILAMENT_COLOR": config.FILAMENT_COLOR,

                # Alternative examples:
                # LINE_COLOR = "#404040"
                # LINE_COLOR = "#00FF00"
                # LINE_COLOR = (0.2, 0.2, 0.2)
            }

            result = vision.analyze(

                image,

                render,

                metadata
            )

            print("\n========== RAW QWEN OUTPUT ==========")
            print(result)
            print("=====================================\n")


            clean = (
                result
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            if not clean:
                print("Qwen returned empty output.")
                continue

            # Remove Qwen formatting wrappers

            clean = result.strip()

            if "```json" in clean:
                clean = clean.split("```json")[1]

            if "```" in clean:
                clean = clean.split("```")[0]

            clean = clean.strip()

            # Remove assistant prefix if present

            if clean.startswith("assistant"):
                clean = clean.replace("assistant", "", 1).strip()


            analysis = json.loads(clean)

            analysis_path = (
                session
                / "analysis"
                / f"{basename}.json"
            )

            with open(
                analysis_path,
                "w"
            ) as f:

                json.dump(
                    analysis,
                    f,
                    indent=4
                )
            print(analysis)

            if(
                not analysis["healthy"]
                and analysis["severity"] >= 5
                and analysis["confidence"] >= 70
            ):
        
                printer.cancel()
                print(
                    "Print cancelled due to detected issue. Beginning Extraction"
                )
                printer.gcode("M140 R30")  # Turn off extruder
                printer.gcode("M190 R30")  # Turn off bed
                printer.gcode("G28")  # Home all axes
                printer.gcode("G1 Y235 Z250 F3000")  # Move Z axis up
                extractor.BrogiBox

            if(
                not analysis["healthy"]
                and analysis["severity"] >= 8
                and analysis["confidence"] >= 70
            ):
        
                printer.cancel()
                print(
                    "Print cancelled due to detected issue. Beginning Extraction"
                )
                printer.gcode("M140 R30")  # Turn off extruder
                printer.gcode("M190 R30")  # Turn off bed
                printer.gcode("G28")  # Home all axes
                printer.gcode("G1 Y235 Z250 F3000")  # Move Z axis up
                extractor.BrogiBox
                

        time.sleep(POLL_INTERVAL)


finally:

    camera.release()
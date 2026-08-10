import time
import config
import os
from panel import InspectionPanel
from camera.webcam import Webcam
from printer.octoprint import OctoPrinter 
from renderer.renderer import GCodeRenderer
from vision.gemini import GeminiVision
try:
    from cobot.extractor import BrogiBox
    from cobot.extractor import NawaPusher
except:
    BrogiBox = None
    NawaPusher = None
from scheduler.layer_scheduler import LayerScheduler
from session import create_session
import json
import re

prompt = config.PROMPT

def extract_json(data):

    if isinstance(data, dict):
        return data

    clean = data.strip()

    if clean.startswith("```"):
        clean = clean.replace("```json", "")
        clean = clean.replace("```", "")
        clean = clean.strip()

    return json.loads(clean)

camera = Webcam(config.CAMERA_INDEX)

printer = OctoPrinter()
renderer = GCodeRenderer(
    config.GCODE_FILE
)
scheduler = LayerScheduler(
    config.INSPECTION_INTERVALS
)

vision = GeminiVision(config.MODEL_NAME)
last_layer = -1
scheduler_initialized = False
filename = printer.filename()

if filename is None:
    filename = "unknown.gcode"

print_name = os.path.splitext(filename)[0]

session, attempt = create_session(print_name)

def handle_print_failure(
    printer,
    print_filename,
    severity
):

    print()
    print("====================================")
    print("PRINT FAILURE CONFIRMED")
    print("====================================")

    print(
        f"Severity: {severity}"
    )

    # Stop current print.
    print("Cancelling print...")
    printer.cancel()

    # Give OctoPrint a moment to process cancellation.
    time.sleep(3)

    # Prepare printer for physical extraction.
    ready = printer.prepare_for_extraction()

    if not ready:

        print(
            "Printer did not reach safe extraction state."
        )

        return False

    # Run robot extraction.
    print(
        "Printer is safe. Starting extraction..."
    )

    NawaPusher()

    print(
        "Extraction complete."
    )

    print(
        f"Restarting print: {print_filename}"
    )

    started = printer.start_print(
        print_filename
    )

    if not started:

        print(
            "Failed to start replacement print."
        )

        return False

    print(
        "Recovery complete. New print started."
    )

    return True

print("System Ready")
panel = InspectionPanel()
panel.update()

try:

    while True:

        state = printer.state()
        panel.update_printer(state)
        panel.update()
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

            if state["state"] == "Printing":

                print(
                    "Print active; waiting for layer information..."
                )

            else:

                print(
                    "Waiting for active print..."
                )

            time.sleep(5)

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

            panel.update_images(
                camera_path=image,
                render_path=render
            )


            panel.update()

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

                "line_color": config.LINE_COLOR,

                "filament_color": config.FILAMENT_COLOR,

            }
            print("Analyzing images...")
            result = vision.analyze(

                image,
                render,
                prompt
            )

            print("\n========== RAW GEMINI OUTPUT ==========")
            print(json.dumps(
                result,
                indent=4
            ))
            print("=====================================\n")


            analysis = None

            for retry in range(3):

                if retry == 0:

                    response = result

                else:

                    print(
                        f"Retrying Gemini analysis ({retry}/2)"
                    )

                    response = vision.analyze(
                        image,
                        render,
                        prompt
                    )


                clean = extract_json(response)


                if clean is None:

                    print(
                        "No JSON detected from Gemini"
                    )

                    continue


                try:

                    if isinstance(clean, dict):
                        analysis = clean
                    else:
                        analysis = json.loads(clean)

                    break


                except json.JSONDecodeError as e:

                    print(
                        "Invalid JSON from Gemini:"
                    )

                    print(clean)

                    print(e)



            if analysis is None:

                print(
                    "Inspection failed after retries. Skipping layer."
                )

                continue

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
            print(json.dumps(
                analysis,
                indent=4
            ))

            panel.update_json(analysis)
            panel.update()

            if (
                not analysis["healthy"]
                and analysis["confidence"] >= 70
                and analysis["severity"] >= 5
            ):

                handled = handle_print_failure(
                    printer,
                    filename,
                    analysis["severity"]
                )

                if handled:

                    print(
                        "Recovery complete. "
                        "New print started."
                    )

                    # Wait until OctoPrint actually reports
                    # the replacement job as Printing.
                    if not printer.wait_for_print_start(filename):

                        print(
                            "Replacement print did not become active."
                        )

                        break

                    # Reset inspection state only AFTER
                    # the replacement print is active.
                    scheduler = LayerScheduler(
                        config.INSPECTION_INTERVALS
                    )

                    scheduler_initialized = False
                    last_layer = -1

                    print(
                        "Waiting for layer information..."
                    )

                    continue
                else:

                    print(
                        "Recovery failed. "
                        "System will not restart print."
                    )

                    break
                            

        time.sleep(config.POLL_INTERVAL)

 
finally:

    camera.release()
    panel.close()
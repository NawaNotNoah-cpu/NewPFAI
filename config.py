# ===========================
# Camera
# ===========================

CAMERA_INDEX = 1

IMAGE_OUTPUT_DIR = "outputs/images"

# ===========================
# AI
# ===========================

MODEL_NAME = "Qwen/Qwen2.5-VL-3B-Instruct"

# ===========================
# OctoPrint
# ===========================

OCTOPRINT_URL = "http://localhost:2960"

API_KEY = "8AMs4cQluTyw8qk8qb0tjNBPEMbVfleJMoPYHPC2QS8"

POLL_INTERVAL = 10.0

# ===========================
# Renderer
# ===========================
 
GCODE_FILE = "testslope.gcode"

RENDER_OUTPUT_DIR = "outputs/renders"

LINE_COLOR = "black"

BACKGROUND_COLOR = "white"

TARGET_LAYER = 300

CAMERA_DISTANCE = 800

# X = pitch
# Y = roll
# Z = yaw
#
CAMERA_PITCH = 0
CAMERA_ROLL = 0
CAMERA_YAW = 0

IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080
DPI = 600

LINE_WIDTH = 1.0

LINE_COLOR = "#FF8000"

# Alternative examples:
# LINE_COLOR = "#404040"
# LINE_COLOR = "#00FF00"
# LINE_COLOR = (0.2, 0.2, 0.2)

# ===========================
# Inspection Scheduler
# ===========================

INSPECTION_INTERVALS = 10

# ===========================
# Qwen Vision
# ===========================

PROMPT = """

Metadata

Print name: {print_name}

Attempt: {attempt}

Current layer: {layer}

Total layers: {total_layers}

Completion: {progress:.1f}%

Current Z Height: {z_height:.2f} mm

The FIRST image is the expected render.

The SECOND image is the actual webcam image.

Only evaluate whether the current printed geometry matches what should exist at THIS layer.

Ignore future geometry.

Determine whether the printed object matches the expected geometry.

Ignore:

- lighting
- color differences
- printer frame
- build plate texture
- camera noise
- background images

Look for:

- spaghetti
- detached print
- missing geometry
- broken appendages
- shifted layers
- severe ringing
- collapsed bridges
- warping
- overhang collapse
- blobs
- under extrusion
- over extrusion
- missing sections
- unexpected objects
- nozzle collisions

A severity level of 0-10 is to be assigned, where 1 is minor and 10 is catastrophic.
Severity 0-2 indicates a healthy print, and the print can continue.
Severity 3-5 indicates a moderate issue, and the print should continue, however, the user should be notified.
Severity 6-7 indicates a significant issue, and the print should be paused for inspection, and the user notified.
Severity 8-10 indicates a severe issue, and the print should be paused immediately.
Return ONLY valid JSON.

    {
        "healthy": true,
        "confidence": 96,
        "severity": 0,
        "failure_type": "none",
        "reason": "Matches expected geometry."
    }


"""
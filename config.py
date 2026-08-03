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
 
GCODE_FILE = "snoopenchy.gcode"

RENDER_OUTPUT_DIR = "outputs/renders"


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

LINE_COLOR = "#3901B1"

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

s
Return ONLY valid JSON. Below is an example of the expected output format. Make the reason much more detailed, including precise image analysis and information regarding the basis for the decision.

    {{
        "healthy": true,
        "confidence": 96,
        "severity": 0,
        "failure_type": "none",
        "reason": "Matches expected geometry."
    }}


"""
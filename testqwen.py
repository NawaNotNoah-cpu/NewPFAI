import json
from pathlib import Path

import config
import os

os.environ["GEMINI_API_KEY"] = config.GEMINI_API_KEY
from vision.gemini import GeminiVision


# ==========================================
# Test Image Directories
# ==========================================
prompt = config.PROMPT

RENDER_IMAGE = Path(
    "qwentest/render.png"
)

WEBCAM_IMAGE = Path(
    "qwentest/capture2.png"
)

OUTPUT_JSON = Path(
    "qwentest/output.json"
)


# ==========================================
# Metadata
# ==========================================

metadata = {
    "print_name": "Prompt Debug",
    "attempt": 1,
    "layer": 124,
    "total_layers": 248,
    "progress": 50.0,
    "z_height": 8.80,
    "line_color": config.LINE_COLOR,
    "filament_color": config.FILAMENT_COLOR,
}


def extract_json(text):

    if isinstance(text, dict):
        return text

    clean = text.strip()

    if clean.startswith("```"):
        clean = clean.replace("```json", "")
        clean = clean.replace("```", "")
        clean = clean.strip()

    return json.loads(clean)


def main():

    print("Loading model...")

    vision = GeminiVision(config.MODEL_NAME)

    print("\nRunning inspection...\n")


    result = vision.analyze(
        WEBCAM_IMAGE,
        RENDER_IMAGE,
        prompt
    )

    print("\n========== RAW OUTPUT ==========\n")
    print(result)
    print("\n===============================\n")

    analysis = extract_json(result)

    OUTPUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(OUTPUT_JSON, "w") as f:
        json.dump(
            analysis,
            f,
            indent=4
        )

    print("\nParsed JSON:\n")

    print(json.dumps(
        analysis,
        indent=4
    ))

    print(f"\nSaved to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
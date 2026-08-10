import os
import json
import config
from google import genai
from google.genai import types


class GeminiVision:

    def __init__(self, model_name=None):

        api_key = config.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "Missing GEMINI_API_KEY"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = model_name or "gemini-3.6-flash"


    def _parse_response(self, text):

        if not text:
            raise ValueError(
                "Gemini returned an empty response."
            )

        text = text.strip()

        # Remove markdown fences if Gemini adds them.
        if text.startswith("```"):

            lines = text.splitlines()

            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            text = "\n".join(lines).strip()

        # Find the JSON object.
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError(
                "Gemini response does not contain a complete JSON object."
            )

        json_text = text[start:end + 1]

        return json.loads(json_text)


    def analyze(
        self,
        rendered_path,
        camera_path,
        prompt
    ):

        with open(rendered_path, "rb") as f:
            rendered_bytes = f.read()

        with open(camera_path, "rb") as f:
            camera_bytes = f.read()


        max_retries = getattr(
            config,
            "MAX_RETRIES",
            3
        )


        last_error = None


        for attempt in range(1, max_retries + 1):

            print(
                f"\nGemini inspection attempt "
                f"{attempt}/{max_retries}"
            )


            # On retries, make the JSON requirement explicit.
            request_prompt = prompt

            if attempt > 1:

                request_prompt += """

IMPORTANT RETRY INSTRUCTION:

The previous response was not valid JSON.

Return exactly ONE complete JSON object.

Do not return Markdown.
Do not return ```json fences.
Do not return commentary.
Do not omit any closing braces or brackets.

Verify that the JSON is syntactically complete before responding.
"""


            try:

                response = self.client.models.generate_content(

                    model=self.model,

                    contents=[

                        types.Part.from_text(
                            text=request_prompt
                        ),

                        types.Part.from_bytes(
                            data=rendered_bytes,
                            mime_type="image/png"
                        ),

                        types.Part.from_bytes(
                            data=camera_bytes,
                            mime_type="image/jpeg"
                        )

                    ],

                    config=types.GenerateContentConfig(
                        temperature=0,
                        response_mime_type="application/json"
                    )
                )


                print(
                    "\n========== RAW GEMINI RESPONSE =========="
                )

                print(response.text)

                print(
                    "=========================================\n"
                )


                result = self._parse_response(
                    response.text
                )


                print(
                    f"Gemini JSON valid on attempt "
                    f"{attempt}/{max_retries}"
                )


                return result


            except (
                json.JSONDecodeError,
                ValueError
            ) as e:

                last_error = e

                print(
                    f"Gemini returned invalid JSON "
                    f"on attempt {attempt}/{max_retries}:"
                )

                print(e)


                if attempt < max_retries:

                    print(
                        "Retrying Gemini inspection..."
                    )

                else:

                    print(
                        "Maximum Gemini retries reached."
                    )


        raise RuntimeError(
            f"Gemini failed to return valid JSON "
            f"after {max_retries} attempts."
        ) from last_error
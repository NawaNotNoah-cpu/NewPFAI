from PIL import Image
from config import *
import torch

from transformers import (
    AutoProcessor,
    Qwen2_5_VLForConditionalGeneration
)


class QwenVision:

    def __init__(self, model_name):

        print("Loading Qwen...")

        self.model = (
            Qwen2_5_VLForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto",
            )
        )

        self.processor = (
            AutoProcessor.from_pretrained(
                model_name,
            )
        )

        print("Qwen ready.")

        if torch.cuda.is_available():

            print(
                "Qwen GPU:",
                torch.cuda.get_device_name(0)
            )

            print(
                "VRAM allocated:",
                round(
                    torch.cuda.memory_allocated() / 1024**3,
                    2
                ),
                "GB"
            )

    def analyze(
        self,
        actual_image,
        expected_image,
        metadata
    ):

        actual = Image.open(
            actual_image
        ).convert("RGB")

        expected = Image.open(
            expected_image
        ).convert("RGB")

        prompt_text = PROMPT.format(
            **metadata
        )

        messages = [
            {
                "role": "user",
                "content": [

                    {
                        "type": "image",
                        "image": expected
                    },

                    {
                        "type": "image",
                        "image": actual
                    },

                    {
                        "type": "text",
                        "text": prompt_text
                    }

                ]
            }
        ]

        prompt = self.processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.processor(
            text=[prompt],
            images=[expected, actual],
            return_tensors="pt",
        )

        # Move inputs to the model's active device
        inputs = {
            key: value.to(self.model.device)
            if hasattr(value, "to")
            else value
            for key, value in inputs.items()
        }

        with torch.inference_mode():

            output = self.model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=False,
            )

        # Don't decode the original prompt.
        input_length = inputs["input_ids"].shape[1]

        generated = output[:, input_length:]

        text = self.processor.batch_decode(
            generated,
            skip_special_tokens=True,
        )[0]

        return text.strip()
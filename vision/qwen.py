from PIL import Image

import torch

from transformers import (
    AutoProcessor,
    Qwen2_5_VLForConditionalGeneration
)


class QwenVision:

    def __init__(self, model_name):

        print("Loading Qwen...")

        self.model = (
            Qwen2_5_VLForConditionalGeneration
            .from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
        )

        self.processor = (
            AutoProcessor.from_pretrained(model_name)
        )

        print("Qwen ready.")

    def analyze(self, image_path):

        image = Image.open(image_path)

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image,
                    },
                    {
                        "type": "text",
                        "text":
                        (
                            "You are inspecting a 3D printer.\n\n"
                            "Describe every object visible., Color, Shape, etc.\n"
                            "List any print failures.\n"
                            "Estimate confidence from 0 to 100%.\n"
                            "\n"
                            "If no failure exists, explicitly say "
                            "'Print appears healthy.'"
                        ),
                    },
                ],
            }
        ]

        prompt = self.processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.processor(
            text=[prompt],
            images=[image],
            return_tensors="pt",
        ).to(self.model.device)

        output = self.model.generate(
            **inputs,
            max_new_tokens=1024,
        )

        text = self.processor.batch_decode(
            output,
            skip_special_tokens=True,
        )[0]

        return text
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

    def analyze(
        self,
        actual_image,
        expected_image,
        metadata
        
    ):

        actual = Image.open(actual_image)
        expected = Image.open(expected_image)

        prompt_text = PROMPT.format(
            **metadata
        )

        messages = [
            {
                "role": "user",
                "content": 
                [

                    {
                        "type":"image",
                        "image":expected
                    },

                    {
                        "type":"image",
                        "image":actual
                    },

                    {
                        "type":"text",
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
            images=[actual,expected],
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
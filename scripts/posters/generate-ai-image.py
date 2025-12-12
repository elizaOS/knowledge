#!/usr/bin/env python3
"""
Generate daily AI image from facts using OpenRouter.
Uses GPT-5.2 to create an image prompt from the day's news summary,
then calls Gemini 3 Pro to generate the actual image.
"""

import os
import json
import base64
import requests
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Config
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL = "openai/gpt-5.2"
IMAGE_MODEL = "google/gemini-3-pro-image-preview"

SCRIPT_DIR = Path(__file__).parent.resolve()
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
FACTS_DIR = WORKSPACE_ROOT / "the-council" / "facts"
OUTPUT_DIR = WORKSPACE_ROOT / "posters"

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def load_facts(date: str = None) -> dict:
    """Load facts JSON for given date or daily.json."""
    if date:
        facts_file = FACTS_DIR / f"{date}.json"
    else:
        facts_file = FACTS_DIR / "daily.json"

    if not facts_file.exists():
        raise FileNotFoundError(f"Facts file not found: {facts_file}")

    logging.info(f"Loading facts from: {facts_file}")
    with open(facts_file) as f:
        return json.load(f)


def generate_image_prompt(facts: dict) -> str:
    """Use LLM to create a detailed image prompt from facts summary."""
    summary = facts.get("overall_summary", "")

    if not summary:
        raise ValueError("No overall_summary found in facts")

    logging.info(f"Generating image prompt from summary: {summary[:100]}...")

    system_prompt = """You are an expert AI art director specializing in creating vivid, detailed image prompts.

Given a summary of today's tech/AI news, create a single compelling image prompt that captures the day's essence.

**Your prompt MUST include these elements:**

1. **Subject/Scene**: A specific, concrete visual scene (not abstract concepts)
   - Could be: futuristic landscapes, cyberpunk cityscapes, symbolic still life, nature-tech fusion, ethereal portraits, surreal compositions

2. **Style Reference**: Pick ONE distinct artistic style:
   - Cinematic photography, Studio Ghibli, ukiyo-e, vaporwave, solarpunk, noir, impressionist, concept art, editorial photography, Y2K aesthetic, retrofuturism

3. **Lighting & Atmosphere**: Specific lighting that sets the mood:
   - Golden hour glow, neon-lit darkness, soft diffused light, dramatic chiaroscuro, bioluminescent, volumetric fog, lens flare

4. **Technical Details**: Add realism with camera/render specs:
   - "shot on 35mm film", "8K render", "shallow depth of field", "macro lens", "wide angle", "tilt-shift"

5. **Color Palette**: Mention 2-3 dominant colors or a palette mood:
   - "deep blues and warm amber", "monochromatic teal", "vibrant neon pink and cyan"

**Rules:**
- NO text, words, letters, logos, or typography in the image
- NO literal depictions of screens, code, or UI
- Be SPECIFIC and CONCRETE, not vague
- One cohesive scene, not multiple disconnected elements
- Keep prompt under 200 words

**Output ONLY the image prompt, nothing else.**"""

    response = requests.post(
        OPENROUTER_ENDPOINT,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": LLM_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Today's tech/AI news summary:\n\n{summary}"
                }
            ]
        },
        timeout=60
    )
    response.raise_for_status()

    result = response.json()
    prompt = result["choices"][0]["message"]["content"].strip()
    logging.info(f"Generated image prompt: {prompt}")
    return prompt


def generate_image(prompt: str) -> bytes:
    """Call image model to generate image, return PNG bytes."""
    logging.info("Calling image generation API...")

    response = requests.post(
        OPENROUTER_ENDPOINT,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": IMAGE_MODEL,
            "modalities": ["image", "text"],
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        },
        timeout=120
    )
    response.raise_for_status()

    result = response.json()

    # Extract base64 image from response
    # Format: response.choices[0].message.images[0].image_url.url
    # URL format: "data:image/png;base64,..."
    try:
        images = result["choices"][0]["message"]["images"]
        if not images:
            raise ValueError("No images in response")

        image_url = images[0]["image_url"]["url"]
        if not image_url.startswith("data:"):
            raise ValueError(f"Unexpected image URL format: {image_url[:50]}")

        # Extract base64 data after the comma
        base64_data = image_url.split(",", 1)[1]
        return base64.b64decode(base64_data)

    except (KeyError, IndexError) as e:
        logging.error(f"Failed to extract image from response: {e}")
        logging.error(f"Response structure: {json.dumps(result, indent=2)[:500]}")
        raise ValueError(f"Failed to extract image from API response: {e}")


def main():
    parser = argparse.ArgumentParser(description="Generate AI image from daily facts")
    parser.add_argument("-d", "--date", help="Date in YYYY-MM-DD format (default: use daily.json)")
    parser.add_argument("-o", "--output", help="Output path (default: posters/YYYY-MM-DD_ai-daily.png)")
    args = parser.parse_args()

    if not OPENROUTER_API_KEY:
        logging.error("OPENROUTER_API_KEY environment variable not set")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        facts = load_facts(args.date)
        date_str = facts.get("briefing_date", datetime.now().strftime("%Y-%m-%d"))

        prompt = generate_image_prompt(facts)
        image_bytes = generate_image(prompt)

        if args.output:
            output_path = Path(args.output)
        else:
            output_path = OUTPUT_DIR / f"{date_str}_ai-daily.png"

        output_path.write_bytes(image_bytes)
        logging.info(f"Saved AI-generated image: {output_path}")

        return 0

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        return 1
    except requests.RequestException as e:
        logging.error(f"API request failed: {e}")
        return 1
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

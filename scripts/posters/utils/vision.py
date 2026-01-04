#!/usr/bin/env python3
"""
Simple image analysis using vision models.

Unix philosophy: does one thing well - analyze an image with a prompt.

Usage:
  # Basic description
  python vision.py image.png

  # Custom prompt
  python vision.py image.png -p "What data is shown?"

  # JSON output
  python vision.py image.png -p "List colors" --json

  # From stdin
  cat image.png | python vision.py - -p "describe"

  # Batch analysis
  for f in *.png; do echo "=== $f ==="; python vision.py "$f" -p "one sentence"; done
"""

import os
import sys
import base64
import argparse
from pathlib import Path

import requests

# Config
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemini-2.5-flash-image-preview"
DEFAULT_PROMPT = "Describe this image in detail."


def load_image_base64(path: Path = None, stdin: bool = False) -> tuple[str, str]:
    """Load image as base64. Returns (data_url, mime_type)."""
    if stdin:
        data = sys.stdin.buffer.read()
        mime_type = "image/png"  # Assume PNG for stdin
    else:
        data = path.read_bytes()
        suffix = path.suffix.lower()
        mime_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        mime_type = mime_types.get(suffix, "image/png")

    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime_type};base64,{b64}", mime_type


def analyze(image_url: str, prompt: str, model: str, json_output: bool, reasoning: bool = False) -> str:
    """Send image to vision model and return response."""
    if json_output:
        prompt = f"{prompt}\n\nRespond with valid JSON only, no markdown."

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
    }

    # Enable reasoning for extended thinking
    if reasoning:
        payload["reasoning"] = {"enabled": True}

    response = requests.post(
        OPENROUTER_ENDPOINT,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=120  # Longer timeout for reasoning
    )
    response.raise_for_status()

    result = response.json()
    return result["choices"][0]["message"]["content"].strip()


def main():
    parser = argparse.ArgumentParser(
        description="Analyze images using vision models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "image",
        help="Image file path (or '-' for stdin)"
    )
    parser.add_argument(
        "-p", "--prompt",
        default=DEFAULT_PROMPT,
        help=f"Analysis prompt (default: '{DEFAULT_PROMPT}')"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Request JSON output from model"
    )
    parser.add_argument(
        "-m", "--model",
        default=DEFAULT_MODEL,
        help=f"Model override (default: {DEFAULT_MODEL})"
    )

    args = parser.parse_args()

    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY not set", file=sys.stderr)
        return 1

    try:
        # Load image
        if args.image == "-":
            image_url, _ = load_image_base64(stdin=True)
        else:
            path = Path(args.image)
            if not path.exists():
                print(f"Error: File not found: {path}", file=sys.stderr)
                return 1
            image_url, _ = load_image_base64(path)

        # Analyze
        result = analyze(image_url, args.prompt, args.model, args.json)
        print(result)
        return 0

    except requests.RequestException as e:
        print(f"API error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

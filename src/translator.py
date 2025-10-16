"""Translate extracted text using Google Gemini API."""

import json
import os

import google.generativeai as genai
from dotenv import load_dotenv

from .translation_prompts import get_translation_prompt


def load_json(json_path):
    """Load JSON file.

    Args:
        json_path: Path to JSON file

    Returns:
        dict: Loaded JSON data
    """
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def save_json(data, json_path):
    """Save JSON file.

    Args:
        data: Dictionary to save
        json_path: Path to save JSON file
    """
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def configure_gemini():
    """Configure Gemini API with API key from environment."""
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY not found or not set. "
            "Please copy .env.example to .env and add your API key."
        )

    genai.configure(api_key=api_key)

    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    return genai.GenerativeModel(model_name)


def translate_with_gemini(data, target_lang, source_lang=None):
    """Translate JSON data using Gemini API with configurable prompts.

    Args:
        data: Dictionary with extracted texts
        target_lang: Target language code (e.g., 'es', 'fr', 'de')
        source_lang: Optional source language code

    Returns:
        dict: Translated data in same JSON structure
    """
    load_dotenv()  # Reload to get translation config
    model = configure_gemini()

    # Get translation style and topic from environment
    style = os.getenv("TRANSLATION_STYLE", "direct")
    topic = os.getenv("TRANSLATION_TOPIC", "general")

    # Generate prompt using configurable template
    json_data = json.dumps(data, ensure_ascii=False, indent=2)
    prompt = get_translation_prompt(
        json_data=json_data,
        target_lang=target_lang,
        source_lang=source_lang,
        style=style,
        topic=topic,
    )

    # Call Gemini API
    response = model.generate_content(prompt)

    # Parse response
    response_text = response.text.strip()

    # Remove markdown code blocks if present
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        # Remove first line (```json or ```)
        lines = lines[1:]
        # Remove last line (```)
        if lines[-1].strip() == "```":
            lines = lines[:-1]
        response_text = "\n".join(lines)

    try:
        translated_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        print("Error: Failed to parse Gemini response as JSON")
        print(f"Response: {response_text[:500]}")
        raise e

    # Validate structure
    if "slides" not in translated_data:
        raise ValueError("Translated data missing 'slides' key")

    if len(translated_data["slides"]) != len(data["slides"]):
        raise ValueError(
            f"Slide count mismatch: original has {len(data['slides'])} slides, "
            f"translated has {len(translated_data['slides'])} slides"
        )

    for i, (orig_slide, trans_slide) in enumerate(zip(data["slides"], translated_data["slides"])):
        if len(orig_slide["texts"]) != len(trans_slide["texts"]):
            raise ValueError(
                f"Text count mismatch in slide {i}: "
                f"original has {len(orig_slide['texts'])} texts, "
                f"translated has {len(trans_slide['texts'])} texts"
            )

    return translated_data


def translate(input_json_path, output_json_path, target_lang, source_lang=None):
    """Main translation function.

    Args:
        input_json_path: Path to input JSON file
        output_json_path: Path to output JSON file
        target_lang: Target language code
        source_lang: Optional source language code
    """
    print(f"Loading {input_json_path}...")
    data = load_json(input_json_path)

    total_texts = sum(len(slide["texts"]) for slide in data["slides"])
    print(f"Translating {total_texts} text elements to {target_lang}...")

    translated_data = translate_with_gemini(data, target_lang, source_lang)

    save_json(translated_data, output_json_path)

    print("✓ Translation complete")
    print(f"✓ Saved to {output_json_path}")

"""Translate extracted text using Google Gemini API."""

import json
import os
import time

import google.generativeai as genai
from dotenv import load_dotenv
from google.api_core import exceptions as google_exceptions

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

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    return genai.GenerativeModel(model_name)


def call_gemini_with_retry(model, prompt, max_retries=5, initial_delay=1):
    """Call Gemini API with intelligent retry logic.

    Respects Retry-After headers from the API and uses exponential backoff as fallback.

    Args:
        model: Gemini model instance
        prompt: Prompt to send to the API
        max_retries: Maximum number of retry attempts (default: 5)
        initial_delay: Initial delay in seconds for fallback (default: 1)

    Returns:
        Response from Gemini API

    Raises:
        Exception: If all retries are exhausted
    """
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response

        except google_exceptions.ResourceExhausted as e:
            # Rate limiting (429) - check for Retry-After header
            if attempt < max_retries - 1:
                # Try to get retry-after from exception metadata
                retry_after = None
                if hasattr(e, "response") and e.response:
                    # Check for Retry-After header in response
                    retry_after = e.response.headers.get("Retry-After")
                    if retry_after:
                        try:
                            wait_time = int(retry_after)
                        except (ValueError, TypeError):
                            wait_time = None

                # Fallback to exponential backoff if no retry-after
                if not retry_after or wait_time is None:
                    wait_time = initial_delay * (2**attempt)

                print(
                    f"⚠ Rate limited by Gemini API. "
                    f"Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(wait_time)
            else:
                print(f"✗ Rate limit exceeded after {max_retries} attempts")
                raise

        except (google_exceptions.ServiceUnavailable, google_exceptions.InternalServerError) as e:
            # Transient server errors - check for Retry-After header
            if attempt < max_retries - 1:
                retry_after = None
                if hasattr(e, "response") and e.response:
                    retry_after = e.response.headers.get("Retry-After")
                    if retry_after:
                        try:
                            wait_time = int(retry_after)
                        except (ValueError, TypeError):
                            wait_time = None

                if not retry_after or wait_time is None:
                    wait_time = initial_delay * (2**attempt)

                print(
                    f"⚠ Gemini API service error. "
                    f"Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(wait_time)
            else:
                print(f"✗ Service error persisted after {max_retries} attempts")
                raise

        except google_exceptions.DeadlineExceeded:
            # Timeout - retry with longer delay
            if attempt < max_retries - 1:
                wait_time = initial_delay * (2 ** (attempt + 1))  # Longer backoff for timeouts
                print(
                    f"⚠ Request timeout. "
                    f"Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(wait_time)
            else:
                print(f"✗ Timeout persisted after {max_retries} attempts")
                raise

        except Exception as e:
            # Other errors - don't retry
            print(f"✗ Gemini API error: {e}")
            raise

    raise Exception(f"Failed after {max_retries} retry attempts")


def translate_with_gemini(data, target_lang, source_lang=None, retry_attempt=0):
    """Translate JSON data using Gemini API with configurable prompts.

    Args:
        data: Dictionary with extracted texts
        target_lang: Target language code (e.g., 'es', 'fr', 'de')
        source_lang: Optional source language code
        retry_attempt: Current retry attempt for structure mismatch (internal use)

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
        retry_attempt=retry_attempt,
    )

    # Get retry settings from environment
    max_retries = int(os.getenv("MAX_RETRIES", "5"))
    initial_delay = int(os.getenv("INITIAL_RETRY_DELAY", "1"))

    # Call Gemini API with retry logic
    response = call_gemini_with_retry(model, prompt, max_retries, initial_delay)

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
        orig_count = len(orig_slide["texts"])
        trans_count = len(trans_slide["texts"])
        if orig_count != trans_count:
            # Structure mismatch detected - show error
            print(f"\n✗ Structure mismatch in slide {i+1}:")
            print(f"  Original texts ({orig_count}):")
            for idx, text in enumerate(orig_slide["texts"][:5]):  # Show first 5
                preview = text[:50] + "..." if len(text) > 50 else text
                print(f"    [{idx}] {repr(preview)}")
            if orig_count > 5:
                print(f"    ... and {orig_count - 5} more")

            print(f"  Translated texts ({trans_count}):")
            for idx, text in enumerate(trans_slide["texts"][:5]):  # Show first 5
                preview = text[:50] + "..." if len(text) > 50 else text
                print(f"    [{idx}] {repr(preview)}")
            if trans_count > 5:
                print(f"    ... and {trans_count - 5} more")

            # Retry with more aggressive prompt if this is first attempt
            max_structure_retries = 2
            if retry_attempt < max_structure_retries:
                print(f"\n⚠ Retrying with stricter prompt (attempt {retry_attempt + 1}/{max_structure_retries})...")
                time.sleep(2)  # Brief delay before retry
                return translate_with_gemini(data, target_lang, source_lang, retry_attempt + 1)

            raise ValueError(
                f"Text count mismatch in slide {i+1} after {max_structure_retries} attempts: "
                f"original has {orig_count} texts, translated has {trans_count} texts. "
                f"Gemini API is merging/splitting text elements. "
                f"Try using 'gemini-2.5-pro' model for better structure preservation."
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

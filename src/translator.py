"""Translate extracted text using Google Gemini API."""

import configparser
import contextlib
import json
import time
from pathlib import Path

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from .translation_prompts import get_translation_prompt


class Config:
    """Configuration manager for reading .ini files."""

    def __init__(self, config_path=None):
        """Initialize configuration.

        Args:
            config_path: Path to config.ini file. If None, searches for config.ini
                        in current directory and parent directories.
        """
        self.config = configparser.ConfigParser()

        config_path = self._find_config_file() if config_path is None else Path(config_path)

        if config_path and config_path.exists():
            self.config.read(config_path)

    def _find_config_file(self):
        """Search for config.ini in current and parent directories.

        Returns:
            Path to config.ini or None if not found
        """
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            config_path = parent / "config.ini"
            if config_path.exists():
                return config_path
        return None

    def get(self, section, key, default=None, value_type=str):
        """Get configuration value.

        Args:
            section: Section name in .ini file
            key: Key name in section
            default: Default value if not found
            value_type: Type to convert value to (str, int, bool)

        Returns:
            Configuration value or default
        """
        try:
            if value_type is bool:
                return self.config.getboolean(section, key)
            elif value_type is int:
                return self.config.getint(section, key)
            else:
                return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default

    def get_gemini_api_key(self):
        """Get Gemini API key.

        Returns:
            str: API key

        Raises:
            ValueError: If API key is not configured
        """
        api_key = self.get("gemini", "api_key")
        if not api_key or api_key == "your_api_key_here":
            raise ValueError(
                "GEMINI API key not found or not set. "
                "Please copy config.ini.example to config.ini and add your API key."
            )
        return api_key

    def get_gemini_model(self):
        """Get Gemini model name."""
        return self.get("gemini", "model", default="gemini-2.5-flash")

    def get_translation_style(self):
        """Get translation style."""
        return self.get("default", "style", default="direct")

    def get_translation_topic(self):
        """Get translation topic."""
        return self.get("default", "topic", default="general")

    def get_max_retries(self):
        """Get maximum retry attempts."""
        return self.get("retry", "max_retries", default=5, value_type=int)

    def get_initial_delay(self):
        """Get initial retry delay in seconds."""
        return self.get("retry", "initial_delay", default=1, value_type=int)

    def get_style_instructions(self, style):
        """Get style-specific instructions from config.

        Args:
            style: Style name (e.g., 'direct', 'formal')

        Returns:
            str: Style instructions or None if not found in config
        """
        section = f"style:{style}"
        return self.get(section, "instructions")

    def get_topic_instructions(self, topic):
        """Get topic-specific instructions from config.

        Args:
            topic: Topic name (e.g., 'diving', 'medical')

        Returns:
            str: Topic instructions or None if not found in config
        """
        section = f"topic:{topic}"
        return self.get(section, "instructions")

    def list_styles(self):
        """List all available styles defined in config.

        Returns:
            list: List of style names
        """
        styles = []
        for section in self.config.sections():
            if section.startswith("style:"):
                style_name = section.split(":", 1)[1]
                styles.append(style_name)
        return styles

    def list_topics(self):
        """List all available topics defined in config.

        Returns:
            list: List of topic names
        """
        topics = []
        for section in self.config.sections():
            if section.startswith("topic:"):
                topic_name = section.split(":", 1)[1]
                topics.append(topic_name)
        return topics


# Global config instance
_config = None


def get_config():
    """Get global config instance.

    Returns:
        Config: Global configuration instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


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
    """Configure Gemini API with API key from config.ini."""
    config = get_config()
    api_key = config.get_gemini_api_key()
    genai.configure(api_key=api_key)

    model_name = config.get_gemini_model()
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
                wait_time = initial_delay * (2**attempt)
                if hasattr(e, "response") and e.response:
                    retry_after = e.response.headers.get("Retry-After")
                    if retry_after:
                        with contextlib.suppress(ValueError, TypeError):
                            wait_time = int(retry_after)

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
                # Default to exponential backoff
                wait_time = initial_delay * (2**attempt)

                # Try to get retry-after from response headers
                if hasattr(e, "response") and e.response:
                    retry_after = e.response.headers.get("Retry-After")
                    if retry_after:
                        with contextlib.suppress(ValueError, TypeError):
                            wait_time = int(retry_after)

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


def translate_with_gemini(
    data, target_lang, source_lang=None, retry_attempt=0, style=None, topic=None
):
    """Translate JSON data using Gemini API with configurable prompts.

    Args:
        data: Dictionary with extracted texts
        target_lang: Target language code (e.g., 'es', 'fr', 'de')
        source_lang: Optional source language code
        retry_attempt: Current retry attempt for structure mismatch (internal use)
        style: Optional translation style override
        topic: Optional translation topic override

    Returns:
        dict: Translated data in same JSON structure
    """
    config = get_config()
    model = configure_gemini()

    # Get translation style and topic - CLI args override config
    if style is None:
        style = config.get_translation_style()
    if topic is None:
        topic = config.get_translation_topic()

    # Generate prompt using configurable template
    json_data = json.dumps(data, ensure_ascii=False, indent=2)
    prompt = get_translation_prompt(
        json_data=json_data,
        target_lang=target_lang,
        source_lang=source_lang,
        style=style,
        topic=topic,
        retry_attempt=retry_attempt,
        config=config,
    )

    # Get retry settings from config
    max_retries = config.get_max_retries()
    initial_delay = config.get_initial_delay()

    # Call Gemini API with retry logic
    response = call_gemini_with_retry(model, prompt, max_retries, initial_delay)

    # Parse response
    response_text = response.text.strip()

    # Remove markdown code blocks if present
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text

    try:
        translated_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        # Show more context around the error
        error_start = max(0, e.pos - 100)
        error_end = min(len(response_text), e.pos + 100)
        error_context = response_text[error_start:error_end]

        print(f"\n✗ JSON parsing error at position {e.pos}:")
        print(f"  {e.msg}")
        print("\nContext around error:")
        print(f"  ...{error_context}...")
        print(f"\nFull response length: {len(response_text)} characters")

        # Retry once with a stricter prompt if this is the first attempt
        if retry_attempt == 0:
            print("\n⚠ Retrying with stricter JSON formatting prompt...")
            time.sleep(2)
            return translate_with_gemini(data, target_lang, source_lang, retry_attempt + 1, style=style, topic=topic)

        raise ValueError(
            f"Failed to parse Gemini response as JSON after {retry_attempt + 1} attempts: {e}\n"
            f"Error at line {e.lineno}, column {e.colno}\n"
            f"Context: ...{error_context}..."
        ) from e

    # Validate structure - support both PPTX (slides) and DOCX (paragraphs)
    structure_key = "slides" if "slides" in data else "paragraphs"
    item_name = "slide" if structure_key == "slides" else "paragraph"

    if len(data[structure_key]) != len(translated_data[structure_key]):
        raise ValueError(
            f"{item_name.capitalize()} count mismatch: original has {len(data[structure_key])} {structure_key}, "
            f"translated has {len(translated_data[structure_key])} {structure_key}"
        )

    for i, (orig_slide, trans_slide) in enumerate(zip(data[structure_key], translated_data[structure_key])):
        orig_count = len(orig_slide["texts"])
        trans_count = len(trans_slide["texts"])
        if orig_count != trans_count:
            # Structure mismatch detected - show error
            print(f"\n✗ Structure mismatch in {item_name} {i + 1}:")
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
                print(
                    f"\n⚠ Retrying with stricter prompt (attempt {retry_attempt + 1}/{max_structure_retries})..."
                )
                time.sleep(2)  # Brief delay before retry
                return translate_with_gemini(data, target_lang, source_lang, retry_attempt + 1, style=style, topic=topic)

            raise ValueError(
                f"Text count mismatch in {item_name} {i + 1} after {max_structure_retries} attempts: "
                f"original has {orig_count} texts, translated has {trans_count} texts. "
                f"Gemini API is merging/splitting text elements. "
                f"Try using 'gemini-2.5-pro' model for better structure preservation."
            )

    return translated_data


def translate(
    input_json_path, output_json_path, target_lang, source_lang=None, style=None, topic=None
):
    """Main translation function.

    Args:
        input_json_path: Path to input JSON file
        output_json_path: Path to output JSON file
        target_lang: Target language code
        source_lang: Optional source language code
        style: Optional translation style override
        topic: Optional translation topic override
    """
    print(f"Loading {input_json_path}...")
    data = load_json(input_json_path)

    # Support both PPTX (slides) and DOCX (paragraphs)
    structure_key = "slides" if "slides" in data else "paragraphs"
    total_texts = sum(len(item["texts"]) for item in data[structure_key])
    print(f"Translating {total_texts} text elements to {target_lang}...")

    translated_data = translate_with_gemini(
        data, target_lang, source_lang, retry_attempt=0, style=style, topic=topic
    )

    save_json(translated_data, output_json_path)

    print("✓ Translation complete")
    print(f"✓ Saved to {output_json_path}")

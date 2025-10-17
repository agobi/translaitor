"""Translation prompt templates for different styles and topics."""

from typing import Union

# Base translation prompt template
BASE_PROMPT = """Translate the following JSON structure{source_lang_text} to {target_lang}.

{style_instructions}

{topic_instructions}

CRITICAL REQUIREMENTS - FOLLOW EXACTLY:
1. Preserve the EXACT JSON structure with "slides" array and "texts" arrays
2. ONLY translate the text content inside the "texts" arrays
3. Do NOT translate the JSON keys ("slides", "texts")
4. Return ONLY valid JSON, no additional text, explanation, or markdown
5. MUST maintain the EXACT same number of slides and text elements
6. EVERY text element in input MUST have EXACTLY ONE corresponding text element in output
7. Do NOT merge, split, or skip any text elements
8. Empty strings "" should remain as empty strings ""
9. Preserve line breaks (\\n) within text elements

VALIDATION:
- Input has {slide_count} slides
- Each slide has a specific number of texts - preserve this EXACTLY
- If input texts array has N elements, output texts array MUST have N elements

Input JSON:
{json_data}

Return the translated JSON (ONLY the JSON, nothing else):"""


# Default fallback instructions (used only if config.ini is missing)
DEFAULT_STYLE_INSTRUCTION = """Translation Style: Use clear, natural language.
- Maintain the original tone and meaning
- Use appropriate grammar and vocabulary
- Keep the translation fluent and readable"""

DEFAULT_TOPIC_INSTRUCTION = ""  # No specific topic guidance by default


def get_translation_prompt(
    json_data,
    target_lang,
    source_lang=None,
    style="direct",
    topic="general",
    retry_attempt=0,
    config=None,
):
    """Generate a translation prompt based on configuration.

    Args:
        json_data: JSON string to translate
        target_lang: Target language code
        source_lang: Optional source language code
        style: Translation style (direct, formal, casual, technical)
        topic: Topic context (diving, medical, technical, business, education, general)
        retry_attempt: Retry attempt number (adds stronger warnings if >0)
        config: Optional Config object to read instructions from INI file

    Returns:
        str: Complete prompt for translation
    """
    import json as json_module

    # Parse JSON to count slides for validation
    slide_count: Union[int, str]
    try:
        data = json_module.loads(json_data)
        slide_count = len(data.get("slides", []))
    except (json_module.JSONDecodeError, KeyError, TypeError):
        slide_count = "unknown"

    # Format source language text
    source_lang_text = f" from {source_lang}" if source_lang else ""

    # Get style instructions - try config first, fallback to default
    style_instructions = None
    if config:
        style_instructions = config.get_style_instructions(style)
    if not style_instructions:
        style_instructions = DEFAULT_STYLE_INSTRUCTION

    # Get topic instructions - try config first, fallback to default
    topic_instructions = None
    if config:
        topic_instructions = config.get_topic_instructions(topic)
    if not topic_instructions:
        topic_instructions = DEFAULT_TOPIC_INSTRUCTION

    # Add extra emphasis on retries
    retry_warning = ""
    if retry_attempt > 0:
        retry_warning = f"""

⚠️  CRITICAL - RETRY ATTEMPT {retry_attempt}:
The previous translation had structure errors (text elements were merged/split).
YOU MUST PRESERVE THE EXACT NUMBER OF TEXT ELEMENTS IN EACH SLIDE.
DO NOT COMBINE ADJACENT TEXT ELEMENTS EVEN IF THEY SEEM RELATED.
TRANSLATE EACH TEXT ELEMENT SEPARATELY AND INDEPENDENTLY.
Count the input texts carefully and ensure output has the EXACT same count."""

    # Build complete prompt
    prompt = BASE_PROMPT.format(
        source_lang_text=source_lang_text,
        target_lang=target_lang,
        style_instructions=style_instructions,
        topic_instructions=topic_instructions,
        slide_count=slide_count,
        json_data=json_data,
    )

    # Append retry warning if needed
    if retry_warning:
        prompt += retry_warning

    return prompt

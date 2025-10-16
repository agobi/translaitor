"""Translation prompt templates for different styles and topics."""

# Base translation prompt template
BASE_PROMPT = """Translate the following JSON structure{source_lang_text} to {target_lang}.

{style_instructions}

{topic_instructions}

CRITICAL REQUIREMENTS:
1. Preserve the EXACT JSON structure with "slides" array and "texts" arrays
2. Only translate the text content inside the "texts" arrays
3. Do NOT translate the JSON keys ("slides", "texts")
4. Return ONLY valid JSON, no additional text or explanation
5. Maintain the same number of slides and text elements

Input JSON:
{json_data}

Return the translated JSON:"""


# Style-specific instructions
STYLE_INSTRUCTIONS = {
    "direct": """Translation Style: Use direct, clear, and concise language.
- Avoid overly formal or flowery language
- Use active voice where possible
- Be straightforward and to the point
- Maintain professional tone while being accessible""",
    "formal": """Translation Style: Use formal, professional language.
- Maintain formal register throughout
- Use complete sentences and proper grammar
- Avoid contractions and colloquialisms
- Use industry-standard terminology""",
    "casual": """Translation Style: Use casual, conversational language.
- Use natural, everyday expressions
- Keep it friendly and approachable
- Use contractions where natural
- Speak directly to the reader""",
    "technical": """Translation Style: Use precise technical language.
- Maintain technical accuracy
- Use exact technical terms
- Preserve all technical specifications
- Keep professional and precise""",
}


# Topic-specific instructions
TOPIC_INSTRUCTIONS = {
    "diving": """Topic Context: This content is about SCUBA diving and deep diving.
- Use correct diving terminology (e.g., "depth", "decompression", "nitrogen narcosis")
- Maintain safety-critical information accurately
- Use terminology recognized by diving certification organizations (PADI, SSI, SDI, etc.)
- Preserve numerical values for depths, times, and safety limits exactly""",
    "medical": """Topic Context: This content is medical/healthcare related.
- Use accurate medical terminology
- Preserve all dosages, measurements, and medical specifications exactly
- Maintain formal medical register
- Use terminology consistent with medical standards""",
    "technical": """Topic Context: This content is technical documentation.
- Preserve all technical terms and specifications
- Maintain accuracy for measurements, codes, and technical details
- Use industry-standard terminology
- Keep technical precision""",
    "business": """Topic Context: This content is business-related.
- Use appropriate business terminology
- Maintain professional tone
- Use terminology common in business contexts
- Preserve numbers, dates, and business-specific terms accurately""",
    "education": """Topic Context: This content is educational material.
- Use clear, pedagogical language
- Maintain instructional tone
- Use terminology appropriate for learners
- Keep explanations accessible""",
}


def get_translation_prompt(
    json_data, target_lang, source_lang=None, style="direct", topic="general"
):
    """Generate a translation prompt based on configuration.

    Args:
        json_data: JSON string to translate
        target_lang: Target language code
        source_lang: Optional source language code
        style: Translation style (direct, formal, casual, technical)
        topic: Topic context (diving, medical, technical, business, education, general)

    Returns:
        str: Complete prompt for translation
    """
    # Format source language text
    source_lang_text = f" from {source_lang}" if source_lang else ""

    # Get style instructions
    style_instructions = STYLE_INSTRUCTIONS.get(style, STYLE_INSTRUCTIONS["direct"])

    # Get topic instructions
    topic_instructions = TOPIC_INSTRUCTIONS.get(topic, "")

    # Build complete prompt
    prompt = BASE_PROMPT.format(
        source_lang_text=source_lang_text,
        target_lang=target_lang,
        style_instructions=style_instructions,
        topic_instructions=topic_instructions,
        json_data=json_data,
    )

    return prompt

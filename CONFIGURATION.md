# Translation Configuration Guide

## Overview

The PPTX translator supports customizable translation prompts to adapt the translation style and domain-specific terminology to your needs.

## Configuration File

Edit `.env` to configure translation behavior:

```bash
# API Configuration
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# Translation Configuration
TRANSLATION_STYLE=direct
TRANSLATION_TOPIC=diving
```

## Translation Styles

### Direct (Recommended for Diving)
**Setting:** `TRANSLATION_STYLE=direct`

Characteristics:
- Clear and concise language
- Active voice where possible
- Straightforward and to the point
- Professional yet accessible

Best for: Training materials, instructions, safety information

### Formal
**Setting:** `TRANSLATION_STYLE=formal`

Characteristics:
- Formal professional language
- Complete sentences and proper grammar
- No contractions or colloquialisms
- Industry-standard terminology

Best for: Official documentation, certifications, legal content

### Casual
**Setting:** `TRANSLATION_STYLE=casual`

Characteristics:
- Conversational language
- Friendly and approachable
- Natural everyday expressions
- Direct communication

Best for: Marketing materials, blog posts, casual presentations

### Technical
**Setting:** `TRANSLATION_STYLE=technical`

Characteristics:
- Precise technical language
- Exact technical terms
- Preserved specifications
- Professional and precise

Best for: Technical manuals, specifications, engineering content

## Translation Topics

### Diving (Default for this project)
**Setting:** `TRANSLATION_TOPIC=diving`

Features:
- Correct diving terminology (depth, decompression, nitrogen narcosis, etc.)
- Safety-critical information preserved accurately
- Terminology recognized by PADI, SSI, SDI, and other certification organizations
- Exact preservation of numerical values (depths, times, safety limits)

Example terms maintained:
- "Decompression stop" → correctly translated with diving context
- "Nitrogen narcosis" → uses standard diving term
- "30 meters" → preserved exactly, not approximated

### Medical
**Setting:** `TRANSLATION_TOPIC=medical`

Features:
- Accurate medical terminology
- Exact preservation of dosages and measurements
- Formal medical register
- Standards-compliant terminology

### Technical
**Setting:** `TRANSLATION_TOPIC=technical`

Features:
- Preserved technical specifications
- Accurate measurements and codes
- Industry-standard terminology
- Technical precision maintained

### Business
**Setting:** `TRANSLATION_TOPIC=business`

Features:
- Appropriate business terminology
- Professional tone
- Accurate numbers and dates
- Business context awareness

### Education
**Setting:** `TRANSLATION_TOPIC=education`

Features:
- Clear pedagogical language
- Instructional tone
- Learner-appropriate terminology
- Accessible explanations

### General
**Setting:** `TRANSLATION_TOPIC=general`

Default translation without specific domain guidance.

## Examples

### Diving Training Material (Recommended)
```bash
TRANSLATION_STYLE=direct
TRANSLATION_TOPIC=diving
```

This will translate "Perform your safety stop at 5 meters for 3 minutes" accurately maintaining:
- Diving terminology ("safety stop")
- Exact measurements (5 meters, 3 minutes)
- Direct, clear instruction style

### Formal Certification Document
```bash
TRANSLATION_STYLE=formal
TRANSLATION_TOPIC=diving
```

Maintains professional formal tone while preserving diving-specific terminology.

### Casual Marketing Content
```bash
TRANSLATION_STYLE=casual
TRANSLATION_TOPIC=diving
```

Friendly tone while still maintaining accurate diving terminology.

## Custom Prompts

Advanced users can modify the prompts in `src/translation_prompts.py` to:
- Add new translation styles
- Add new topic domains
- Customize existing prompts
- Add organization-specific terminology

See `src/translation_prompts.py` for the full prompt templates.

## Testing Configuration

After changing configuration:

1. Test with a small sample slide first
2. Verify terminology accuracy
3. Check that safety-critical information is preserved
4. Confirm the tone matches your needs

```bash
python cli.py translate-pptx sample.pptx output.pptx --target-lang es
# Review output.pptx before processing larger files
```

## Best Practices

1. **Always use `diving` topic for dive training materials** - ensures correct technical terminology
2. **Use `direct` style for training** - clearest for instruction and safety
3. **Test with sample content first** - verify configuration before large batches
4. **Keep safety information exact** - numerical values are always preserved
5. **Review translated content** - especially for certification materials

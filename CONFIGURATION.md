# Translation Configuration Guide

## Overview

The PPTX translator supports customizable translation prompts to adapt the translation style and domain-specific terminology to your needs.

## Configuration File

Edit `.env` to configure translation behavior:

### Example Configuration for Diving Content

```bash
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
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

## Retry Configuration

The translator includes intelligent automatic retry logic that prioritizes API guidance while providing robust fallback strategies.

### How It Works

The retry system uses a **two-tier approach**:

#### 1. API-Guided Retry (Primary)

When Gemini API returns rate limit or service errors, it may include a `Retry-After` header that tells you exactly when to retry:

```
Rate Limited → Check Retry-After header → Wait exact time → Retry
```

**Example:**
- API returns 429 (rate limited) with `Retry-After: 3`
- System waits exactly 3 seconds
- Retries the request

This is **optimal** because:
- Respects API's current load and capacity
- Minimizes unnecessary waiting
- Complies with API's rate limiting strategy

#### 2. Exponential Backoff (Fallback)

If no `Retry-After` header is provided, uses exponential backoff:

```
1st retry: 1s → 2nd: 2s → 3rd: 4s → 4th: 8s → 5th: 16s
```

### Default Behavior

- **Max Retries**: 5 attempts
- **Initial Delay**: 1 second (for fallback)
- **Primary Strategy**: Respects API `Retry-After` headers
- **Fallback Strategy**: Exponential backoff
- **Smart**: Always uses API guidance when available

### Handles These Errors Automatically

1. **Rate Limiting (429)** - Reads `Retry-After`, falls back to exponential backoff
2. **Service Unavailable (503)** - Reads `Retry-After`, falls back to exponential backoff
3. **Timeout Errors** - Uses exponential backoff (no header expected)
4. **Internal Server Errors (500)** - Reads `Retry-After`, falls back to exponential backoff
5. **Other Errors** - Fails immediately (no retry)

### Custom Configuration

Set in `.env` file:

```bash
# Retry Configuration (optional)
MAX_RETRIES=5              # Number of retry attempts (default: 5)
INITIAL_RETRY_DELAY=1      # Initial delay in seconds (default: 1)
```

### Example Backoff Timeline

With default settings (5 retries, 1s initial delay):
- Attempt 1: Immediate
- Attempt 2: Wait 1s
- Attempt 3: Wait 2s
- Attempt 4: Wait 4s
- Attempt 5: Wait 8s
- Attempt 6: Wait 16s

Total maximum wait time: ~31 seconds

### When to Adjust

**Increase retries (`MAX_RETRIES=10`):**
- Processing large batches
- During peak API usage hours
- For critical production workflows

**Increase delay (`INITIAL_RETRY_DELAY=2`):**
- Frequent rate limiting
- Large files causing longer processing
- Conservative approach to avoid API abuse

## Best Practices

1. **Always use `diving` topic for dive training materials** - ensures correct technical terminology
2. **Use `direct` style for training** - clearest for instruction and safety
3. **Test with sample content first** - verify configuration before large batches
4. **Keep safety information exact** - numerical values are always preserved
5. **Review translated content** - especially for certification materials
6. **Monitor retry messages** - Adjust retry settings if you see frequent rate limiting

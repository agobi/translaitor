# PPTX Slide Translator

Translate PowerPoint presentations using Google Gemini API.

## Features

- Extract text from PPTX files to structured JSON
- Translate text using Google Gemini
- Reintegrate translated text back into PPTX
- CLI-based workflow

## Setup

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure API key and translation settings:**
```bash
cp .env.example .env
# Edit .env and configure:
# - GEMINI_API_KEY: Your Gemini API key (required)
# - TRANSLATION_STYLE: Translation style (direct, formal, casual, technical)
# - TRANSLATION_TOPIC: Content topic (diving, medical, technical, business, education, general)
```

## Usage

### Quick Translation (Full Pipeline)
```bash
python cli.py translate-pptx input.pptx output.pptx --target-lang es
```

### Step-by-Step Workflow

1. **Extract text to JSON:**
```bash
python cli.py extract input.pptx extracted.json
```

2. **Translate JSON:**
```bash
python cli.py translate extracted.json translated.json --target-lang es
```

3. **Reintegrate into PPTX:**
```bash
python cli.py reintegrate input.pptx translated.json output.pptx
```

## Commands

- `extract <input.pptx> <output.json>` - Extract text from PPTX
- `translate <input.json> <output.json> --target-lang <lang>` - Translate JSON
- `reintegrate <original.pptx> <translated.json> <output.pptx>` - Create translated PPTX
- `translate-pptx <input.pptx> <output.pptx> --target-lang <lang>` - Full pipeline

## Configuration

### Translation Styles

Configure `TRANSLATION_STYLE` in `.env`:
- **direct** (default): Clear, concise, straightforward language
- **formal**: Professional, complete sentences, formal register
- **casual**: Conversational, friendly, approachable tone
- **technical**: Precise technical language with exact terminology

### Translation Topics

Configure `TRANSLATION_TOPIC` in `.env`:
- **diving** (recommended for diving content): Maintains correct diving terminology, safety-critical information
- **medical**: Accurate medical terminology and specifications
- **technical**: Technical documentation with precise specifications
- **business**: Business terminology and professional tone
- **education**: Clear pedagogical language for learners
- **general** (default): Standard translation without topic-specific guidance

### Example Configuration for Diving Content

```bash
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash
TRANSLATION_STYLE=direct
TRANSLATION_TOPIC=diving
```

This configuration will:
- Use direct, clear language
- Maintain correct diving terminology (depth, decompression, etc.)
- Preserve safety-critical numerical values
- Use terminology recognized by diving organizations

## Requirements

- Python 3.8+
- Google Gemini API key

## License

MIT

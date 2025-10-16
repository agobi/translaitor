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

3. **Configure API key:**
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
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

## Requirements

- Python 3.8+
- Google Gemini API key

## License

MIT

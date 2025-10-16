# Quick Start Guide

## Setup (One-time)

```bash
# Run the setup script
./setup.sh

# Edit .env and add your Gemini API key
nano .env  # or use your preferred editor

# Activate virtual environment
source venv/bin/activate
```

## Usage Examples

### Quick Translation (Recommended)
Translate entire PPTX in one command:
```bash
python cli.py translate-pptx presentation.pptx presentation_es.pptx --target-lang es
```

### Step-by-Step Workflow
If you want to inspect or manually edit the extracted text:

```bash
# 1. Extract text to JSON
python cli.py extract presentation.pptx extracted.json

# 2. Translate the JSON
python cli.py translate extracted.json translated.json --target-lang es

# 3. Create translated PPTX
python cli.py reintegrate presentation.pptx translated.json presentation_es.pptx
```

### Testing Without Translation
Test that extraction and reintegration work:
```bash
# Extract
python cli.py extract input.pptx test.json

# Reintegrate without translation (should produce identical output)
python cli.py reintegrate input.pptx test.json output.pptx
```

## Language Codes

Common language codes for `--target-lang`:
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `ja` - Japanese
- `zh` - Chinese
- `ko` - Korean
- `ar` - Arabic
- `ru` - Russian

## Project Structure

```
slidetranslator/
├── cli.py              # Main CLI entry point
├── src/
│   ├── extractor.py    # Extract text from PPTX → JSON
│   ├── translator.py   # Translate using Gemini API
│   ├── reintegrator.py # Reintegrate text → PPTX
│   └── utils.py        # Helper functions
├── requirements.txt    # Python dependencies
├── .env               # Your API keys (not in git)
└── README.md          # Full documentation
```

## Troubleshooting

### "GEMINI_API_KEY not found"
- Make sure you copied `.env.example` to `.env`
- Add your actual API key to the `.env` file
- Verify the key has no extra spaces or quotes

### Virtual environment not activated
```bash
source venv/bin/activate
```

### Module not found errors
```bash
pip install -r requirements.txt
```

### Text count mismatch warning
This can happen if the PPTX has complex shapes. The tool will still work, but you may want to manually verify the output.

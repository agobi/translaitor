# Quick Start Guide

## Setup (One-time)

```bash
# Run the setup script
./setup.sh

# Edit config.ini and configure:
# - Add your Gemini API key (required)
# - model=gemini-2.5-flash (default, best price-performance)
# - Set style=direct (for clear language)
# - Set topic=diving (for diving content)
nano config.ini  # or use your preferred editor

# Activate virtual environment
source venv/bin/activate
```

## Usage Examples

### Quick Translation (Recommended)

**Single file:**
```bash
python cli.py translate-pptx presentation.pptx presentation_es.pptx --target-lang es
```

**Entire directory:**
```bash
python cli.py translate-dir EN/ ES/ --target-lang es
```

This will:
- Find all .pptx files in EN/ folder
- Translate each one to Spanish
- Save translated files to ES/ folder with same filenames
- Show progress and summary
- Automatically handle rate limits with smart retry logic
- **Error if output files already exist** (safety feature)

**Directory with subdirectories:**
```bash
python cli.py translate-dir EN/ ES/ --target-lang es --recursive
```

**Resume interrupted batch (skip existing):**
```bash
python cli.py translate-dir EN/ ES/ --target-lang es --skip
```
Skips files that already exist in output directory. Useful for resuming interrupted batches.

**Re-translate everything (overwrite existing):**
```bash
python cli.py translate-dir EN/ ES/ --target-lang es --overwrite
```
Overwrites existing files. Use this to re-translate with updated settings.

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
├── config.ini         # Your configuration (not in git)
└── README.md          # Full documentation
```

## Retry Logic

If you see messages like:
```
⚠ Rate limited by Gemini API. Retrying in 3s... (attempt 1/5)
```

This is **normal** during batch processing. The tool automatically:
- Reads the API's recommended wait time
- Waits the appropriate duration
- Retries the request
- Continues with the next file

No action needed - just wait for the retry to complete!

## Troubleshooting

### "GEMINI API key not found"
- Make sure you copied `config.ini.example` to `config.ini`
- Add your actual API key to the `config.ini` file under `[gemini]` section
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

### Frequent rate limiting
If you see many retry messages:
- Increase `max_retries` in `config.ini` under `[retry]` section (e.g., `max_retries = 10`)
- Slow down batch processing
- Consider using Gemini Pro with higher rate limits

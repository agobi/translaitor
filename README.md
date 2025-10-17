<div align="center">
  <img src="./logo.png" alt="translaitor logo" width="200"/>
  
  # translaitor

  > ⚠️ **Disclaimer**: This project is 100% vibe coded. I have no idea what it does, but it seems to work. Use at your own risk! 🎲

  [![Lint and Type Check](https://github.com/agobi/translaitor/actions/workflows/lint.yml/badge.svg)](https://github.com/agobi/translaitor/actions/workflows/lint.yml)
</div>

Translate PowerPoint presentations using Google Gemini API.

## Features

- Extract text from PPTX files to structured JSON (preserves formatting per run)
- Translate text using Google Gemini with intelligent retry logic
- Reintegrate translated text back into PPTX (preserves fonts, colors, sizes)
- CLI-based workflow with batch directory processing
- Configurable translation styles and domain-specific terminology
- Smart retry logic that respects API `Retry-After` headers with exponential backoff fallback
- Automatic handling of rate limits, timeouts, and transient errors

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
# - GEMINI_MODEL: Model to use (default: gemini-2.5-flash)
# - TRANSLATION_STYLE: Translation style (direct, formal, casual, technical)
# - TRANSLATION_TOPIC: Content topic (diving, medical, technical, business, education, general)
```

## Usage

### Quick Translation (Full Pipeline)
```bash
# Single file
python cli.py translate-pptx input.pptx output.pptx --target-lang es

# Entire directory
python cli.py translate-dir input_folder/ output_folder/ --target-lang es

# Directory with subdirectories
python cli.py translate-dir input_folder/ output_folder/ --target-lang es --recursive

# Skip files that already exist
python cli.py translate-dir input_folder/ output_folder/ --target-lang es --skip

# Overwrite existing files
python cli.py translate-dir input_folder/ output_folder/ --target-lang es --overwrite
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

The CLI uses Click for a modern, user-friendly interface with automatic help generation and validation.

- **`extract`** - Extract text from PPTX to JSON
- **`translate`** - Translate JSON using Gemini API  
- **`reintegrate`** - Reintegrate translated text into PPTX
- **`translate-pptx`** - Full translation pipeline for single file (recommended)
- **`translate-dir`** - Batch translate all PPTX files in a directory

Get help for any command:
```bash
python cli.py --help
python cli.py translate-pptx --help
python cli.py translate-dir --help
```

## Retry Logic and Error Handling

The translator includes intelligent retry logic to handle API rate limits and transient errors gracefully:

### How It Works

1. **API-First Approach**: Checks for `Retry-After` header from Gemini API
   - If provided, waits the exact time recommended by the API
   - Example: API says "retry in 3 seconds", we wait exactly 3 seconds

2. **Exponential Backoff Fallback**: If no header is provided
   - 1st retry: 1 second
   - 2nd retry: 2 seconds
   - 3rd retry: 4 seconds
   - 4th retry: 8 seconds
   - 5th retry: 16 seconds

3. **Automatic Error Handling**:
   - **Rate Limiting (429)**: Automatically retries with smart timing
   - **Service Errors (503/500)**: Handles temporary server issues
   - **Timeouts**: Retries with longer delays
   - **Other Errors**: Fails fast without retrying

### Example Output

```bash
[2/10] Processing: Chapter_2.pptx
  ⚠ Rate limited by Gemini API. Retrying in 3s... (attempt 1/5)
  ✓ Success: Chapter_2.pptx
```

### Configuration

Adjust retry behavior in `.env`:

```bash
MAX_RETRIES=5              # Number of retry attempts (default: 5)
INITIAL_RETRY_DELAY=1      # Initial delay for fallback (default: 1)
```

For detailed retry configuration, see [CONFIGURATION.md](CONFIGURATION.md#retry-configuration).

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

## Development

### Linting and Type Checking

The project uses Ruff for linting/formatting and mypy for type checking.

**Install development dependencies:**
```bash
pip install -r requirements-dev.txt
```

**Available commands:**
```bash
# Check code with ruff
make lint

# Auto-format code with ruff
make format

# Type check with mypy
make type-check

# Run all checks
make check
```

**Or use directly:**
```bash
# Ruff
ruff check .          # Check for issues
ruff format .         # Format code
ruff check --fix .    # Auto-fix issues

# Mypy
mypy src/ cli.py
```

### Configuration

All linting and type checking configuration is in `pyproject.toml`:
- **Ruff**: Line length 100, Python 3.8+, common rule sets enabled
- **Mypy**: Type checking with imports ignored for third-party libs

## Requirements

- Python 3.8+
- Google Gemini API key

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

All pull requests are automatically checked with GitHub Actions for:
- Ruff linting and formatting
- Mypy type checking

Make sure to run `make check` before submitting a PR.

## License

BSD 3-Clause License - see [LICENSE](LICENSE) for details.

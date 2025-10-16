#!/usr/bin/env python3
"""CLI for PPTX slide translator."""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src import extractor, translator, reintegrator


def cmd_extract(args):
    """Execute extract command."""
    try:
        extractor.extract(args.input, args.output)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


def cmd_translate(args):
    """Execute translate command."""
    try:
        translator.translate(
            args.input,
            args.output,
            args.target_lang,
            args.source_lang
        )
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


def cmd_reintegrate(args):
    """Execute reintegrate command."""
    try:
        reintegrator.reintegrate(
            args.original,
            args.translated_json,
            args.output
        )
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


def cmd_translate_pptx(args):
    """Execute full translation pipeline."""
    import tempfile
    
    try:
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_extract:
            extracted_path = tmp_extract.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_translate:
            translated_path = tmp_translate.name
        
        print(f"Step 1/3: Extracting text from {args.input}...")
        extractor.extract(args.input, extracted_path)
        
        print(f"\nStep 2/3: Translating to {args.target_lang}...")
        translator.translate(
            extracted_path,
            translated_path,
            args.target_lang,
            args.source_lang
        )
        
        print(f"\nStep 3/3: Creating translated PPTX...")
        reintegrator.reintegrate(
            args.input,
            translated_path,
            args.output
        )
        
        # Cleanup temp files
        os.unlink(extracted_path)
        os.unlink(translated_path)
        
        print(f"\n✓ Translation complete: {args.output}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        # Cleanup temp files on error
        try:
            if 'extracted_path' in locals():
                os.unlink(extracted_path)
            if 'translated_path' in locals():
                os.unlink(translated_path)
        except:
            pass
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Translate PowerPoint presentations using Google Gemini',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full translation pipeline
  %(prog)s translate-pptx input.pptx output.pptx --target-lang es
  
  # Step-by-step workflow
  %(prog)s extract input.pptx extracted.json
  %(prog)s translate extracted.json translated.json --target-lang es
  %(prog)s reintegrate input.pptx translated.json output.pptx
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Extract command
    parser_extract = subparsers.add_parser(
        'extract',
        help='Extract text from PPTX to JSON'
    )
    parser_extract.add_argument('input', help='Input PPTX file')
    parser_extract.add_argument('output', help='Output JSON file')
    parser_extract.set_defaults(func=cmd_extract)
    
    # Translate command
    parser_translate = subparsers.add_parser(
        'translate',
        help='Translate JSON using Gemini API'
    )
    parser_translate.add_argument('input', help='Input JSON file')
    parser_translate.add_argument('output', help='Output JSON file')
    parser_translate.add_argument(
        '--target-lang',
        required=True,
        help='Target language code (e.g., es, fr, de)'
    )
    parser_translate.add_argument(
        '--source-lang',
        help='Source language code (optional)'
    )
    parser_translate.set_defaults(func=cmd_translate)
    
    # Reintegrate command
    parser_reintegrate = subparsers.add_parser(
        'reintegrate',
        help='Reintegrate translated text into PPTX'
    )
    parser_reintegrate.add_argument('original', help='Original PPTX file')
    parser_reintegrate.add_argument('translated_json', help='Translated JSON file')
    parser_reintegrate.add_argument('output', help='Output PPTX file')
    parser_reintegrate.set_defaults(func=cmd_reintegrate)
    
    # Translate PPTX command (full pipeline)
    parser_translate_pptx = subparsers.add_parser(
        'translate-pptx',
        help='Translate PPTX file (full pipeline)'
    )
    parser_translate_pptx.add_argument('input', help='Input PPTX file')
    parser_translate_pptx.add_argument('output', help='Output PPTX file')
    parser_translate_pptx.add_argument(
        '--target-lang',
        required=True,
        help='Target language code (e.g., es, fr, de)'
    )
    parser_translate_pptx.add_argument(
        '--source-lang',
        help='Source language code (optional)'
    )
    parser_translate_pptx.set_defaults(func=cmd_translate_pptx)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()

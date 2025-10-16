#!/usr/bin/env python3
"""CLI for PPTX slide translator."""

import sys
import os
import tempfile
from pathlib import Path
import click

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src import extractor, translator, reintegrator


@click.group()
@click.version_option(version='1.0.0', prog_name='PPTX Translator')
def cli():
    """Translate PowerPoint presentations using Google Gemini.
    
    Examples:
    
      # Full translation pipeline
      python cli.py translate-pptx input.pptx output.pptx --target-lang es
      
      # Step-by-step workflow
      python cli.py extract input.pptx extracted.json
      python cli.py translate extracted.json translated.json --target-lang es
      python cli.py reintegrate input.pptx translated.json output.pptx
    """
    pass


@cli.command()
@click.argument('input', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
def extract(input, output):
    """Extract text from PPTX to JSON."""
    try:
        extractor.extract(input, output)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command()
@click.argument('input', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
@click.option('--target-lang', required=True, help='Target language code (e.g., es, fr, de)')
@click.option('--source-lang', default=None, help='Source language code (optional)')
def translate(input, output, target_lang, source_lang):
    """Translate JSON using Gemini API."""
    try:
        translator.translate(input, output, target_lang, source_lang)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command()
@click.argument('original', type=click.Path(exists=True))
@click.argument('translated_json', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
def reintegrate(original, translated_json, output):
    """Reintegrate translated text into PPTX."""
    try:
        reintegrator.reintegrate(original, translated_json, output)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg='red', err=True)
        sys.exit(1)


@cli.command('translate-pptx')
@click.argument('input', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
@click.option('--target-lang', required=True, help='Target language code (e.g., es, fr, de)')
@click.option('--source-lang', default=None, help='Source language code (optional)')
def translate_pptx(input, output, target_lang, source_lang):
    """Translate PPTX file (full pipeline)."""
    try:
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_extract:
            extracted_path = tmp_extract.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_translate:
            translated_path = tmp_translate.name
        
        click.echo(f"Step 1/3: Extracting text from {input}...")
        extractor.extract(input, extracted_path)
        
        click.echo(f"\nStep 2/3: Translating to {target_lang}...")
        translator.translate(extracted_path, translated_path, target_lang, source_lang)
        
        click.echo("\nStep 3/3: Creating translated PPTX...")
        reintegrator.reintegrate(input, translated_path, output)
        
        # Cleanup temp files
        os.unlink(extracted_path)
        os.unlink(translated_path)
        
        click.secho(f"\n✓ Translation complete: {output}", fg='green')
        
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg='red', err=True)
        # Cleanup temp files on error
        try:
            if 'extracted_path' in locals():
                os.unlink(extracted_path)
            if 'translated_path' in locals():
                os.unlink(translated_path)
        except Exception:
            pass
        sys.exit(1)


if __name__ == '__main__':
    cli()

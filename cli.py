#!/usr/bin/env python3
"""CLI for PPTX slide translator."""

import os
import sys
import tempfile
from pathlib import Path

import click

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src import translator
from src.docx_handler import DOCXHandler
from src.pptx_handler import PPTXHandler


def get_handler_for_file(file_path):
    """Get appropriate handler based on file extension.

    Args:
        file_path: Path to the file

    Returns:
        Handler instance (PPTXHandler or DOCXHandler)

    Raises:
        ValueError: If file type is not supported
    """
    file_path = str(file_path).lower()

    if file_path.endswith('.pptx'):
        return PPTXHandler()
    elif file_path.endswith('.docx'):
        return DOCXHandler()
    else:
        raise ValueError(
            "Unsupported file type. "
            "Supported formats: .pptx (PowerPoint), .docx (Word)"
        )


def get_target_lang(target_lang):
    """Get target language from args or config."""
    if target_lang:
        return target_lang

    # Try to read from config
    try:
        from src.translator import get_config

        config = get_config()
        default_lang = config.get("default", "target_lang")
        if default_lang:
            return default_lang
    except Exception:
        pass

    # If no config default, raise error
    click.secho(
        "✗ Error: --target-lang is required (or set target_lang in [default] section of config.ini)",
        fg="red",
        err=True,
    )
    sys.exit(1)


@click.group()
@click.version_option(version="1.0.0", prog_name="translaitor")
def cli():
    """Translate PowerPoint presentations using Google Gemini.

    Examples:

      # Full translation pipeline
      python cli.py translate input.pptx output.pptx --target-lang es

      # Step-by-step workflow
      python cli.py extract input.pptx extracted.json
      python cli.py translate-json extracted.json translated.json --target-lang es
      python cli.py reintegrate input.pptx translated.json output.pptx
    """
    pass


@cli.command("extract")
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
def extract(input, output):
    """Extract text from document (PPTX/DOCX) to JSON."""
    try:
        handler = get_handler_for_file(input)
        handler.extract(input, output)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


@cli.command("translate-json")
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option(
    "--target-lang",
    default=None,
    help="Target language code (e.g., es, fr, de, default from config)",
)
@click.option("--source-lang", default=None, help="Source language code (optional)")
@click.option(
    "--style", default=None, help="Translation style (direct, formal, casual, technical, gen-alpha)"
)
@click.option(
    "--topic",
    default=None,
    help="Translation topic (diving, medical, technical, business, education, general)",
)
def translate_json(input, output, target_lang, source_lang, style, topic):
    """Translate JSON file using Gemini API."""
    try:
        target_lang = get_target_lang(target_lang)
        translator.translate(input, output, target_lang, source_lang, style=style, topic=topic)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


@cli.command("reintegrate")
@click.argument("original", type=click.Path(exists=True))
@click.argument("translated_json", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
def reintegrate(original, translated_json, output):
    """Reintegrate translated JSON back into document (PPTX/DOCX)."""
    try:
        handler = get_handler_for_file(original)
        handler.reintegrate(original, translated_json, output)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


@cli.command("translate")
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option(
    "--target-lang",
    default=None,
    help="Target language code (e.g., es, fr, de, default from config)",
)
@click.option("--source-lang", default=None, help="Source language code (optional)")
@click.option(
    "--style", default=None, help="Translation style (direct, formal, casual, technical, gen-alpha)"
)
@click.option(
    "--topic",
    default=None,
    help="Translation topic (diving, medical, technical, business, education, general)",
)
def translate(input, output, target_lang, source_lang, style, topic):
    """Translate document (PPTX/DOCX) - full pipeline."""
    try:
        target_lang = get_target_lang(target_lang)
        handler = get_handler_for_file(input)

        # Create temporary files
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_extract:
            extracted_path = tmp_extract.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_translate:
            translated_path = tmp_translate.name

        click.echo(f"Step 1/3: Extracting text from {input}...")
        handler.extract(input, extracted_path)

        click.echo(f"\nStep 2/3: Translating to {target_lang}...")
        translator.translate(
            extracted_path, translated_path, target_lang, source_lang, style=style, topic=topic
        )

        click.echo("\nStep 3/3: Creating translated document...")
        handler.reintegrate(input, translated_path, output)

        # Cleanup temp files
        os.unlink(extracted_path)
        os.unlink(translated_path)

        click.secho(f"\n✓ Translation complete: {output}", fg="green")

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        # Cleanup temp files on error
        try:
            if "extracted_path" in locals():
                os.unlink(extracted_path)
            if "translated_path" in locals():
                os.unlink(translated_path)
        except Exception:
            pass
        sys.exit(1)


@cli.command("translate-dir")
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument("output_dir", type=click.Path())
@click.option(
    "--target-lang",
    default=None,
    help="Target language code (e.g., es, fr, de, default from config)",
)
@click.option("--source-lang", default=None, help="Source language code (optional)")
@click.option(
    "--style", default=None, help="Translation style (direct, formal, casual, technical, gen-alpha)"
)
@click.option(
    "--topic",
    default=None,
    help="Translation topic (diving, medical, technical, business, education, general)",
)
@click.option(
    "--recursive/--no-recursive", default=False, help="Process subdirectories recursively"
)
@click.option(
    "--skip",
    "skip_existing",
    is_flag=True,
    help="Skip files that already exist in output directory",
)
@click.option(
    "--overwrite",
    "overwrite_existing",
    is_flag=True,
    help="Overwrite existing files in output directory",
)
def translate_dir(
    input_dir,
    output_dir,
    target_lang,
    source_lang,
    style,
    topic,
    recursive,
    skip_existing,
    overwrite_existing,
):
    """Translate all documents (PPTX/DOCX) in a directory.

    This will:
    - Find all .pptx files in the input directory
    - Translate each one to the target language
    - Save translated files to output directory with same filenames
    - Continue processing even if individual files fail
    """
    target_lang = get_target_lang(target_lang)

    # Check for conflicting flags
    if skip_existing and overwrite_existing:
        click.secho("✗ Error: Cannot use both --skip and --overwrite together", fg="red", err=True)
        sys.exit(1)

    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all supported document files (PPTX and DOCX)
    if recursive:
        doc_files = list(input_path.rglob("*.pptx")) + list(input_path.rglob("*.docx"))
    else:
        doc_files = list(input_path.glob("*.pptx")) + list(input_path.glob("*.docx"))

    if not doc_files:
        click.secho(f"✗ No document files (PPTX/DOCX) found in {input_dir}", fg="yellow")
        return

    # Check for existing files if not overwriting or skipping
    if not skip_existing and not overwrite_existing:
        existing_files = []
        for doc_file in doc_files:
            rel_path = doc_file.relative_to(input_path)
            output_file = output_path / rel_path
            if output_file.exists():
                existing_files.append(str(rel_path))

        if existing_files:
            click.secho(
                f"\n✗ Error: {len(existing_files)} file(s) already exist in output directory:",
                fg="red",
            )
            for file in existing_files[:10]:  # Show first 10
                click.echo(f"  - {file}")
            if len(existing_files) > 10:
                click.echo(f"  ... and {len(existing_files) - 10} more")
            click.echo("\nOptions:")
            click.echo("  --skip      Skip existing files and translate only new ones")
            click.echo("  --overwrite Overwrite existing files")
            sys.exit(1)

    click.echo(f"Found {len(doc_files)} document file(s) to translate")
    click.echo(f"Target language: {target_lang}")
    click.echo(f"Output directory: {output_dir}")
    if skip_existing:
        click.echo("Mode: Skip existing files")
    elif overwrite_existing:
        click.echo(f"\nTranslating {len(doc_files)} files to {target_lang}...\n")

    successful = 0
    skipped = 0
    failed = 0
    failed_files = []

    for doc_file in doc_files:
        rel_path = doc_file.relative_to(input_path)
        output_file = output_path / rel_path

        # Check if output file exists and handle based on flags
        if output_file.exists() and skip_existing:
            click.echo(f"Skipping: {rel_path} (already exists)")
            skipped += 1
            continue

        # Create subdirectories in output if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)

        click.echo(f"Processing: {rel_path}")

        try:
            # Get appropriate handler for this file type
            handler = get_handler_for_file(str(doc_file))

            # Create temporary files
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_extract:
                extracted_path = tmp_extract.name

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as tmp_translate:
                translated_path = tmp_translate.name

            # Extract
            handler.extract(str(doc_file), extracted_path)

            # Translate
            translator.translate(
                extracted_path, translated_path, target_lang, source_lang, style=style, topic=topic
            )

            # Reintegrate
            handler.reintegrate(str(doc_file), translated_path, str(output_file))

            # Cleanup temp files
            os.unlink(extracted_path)
            os.unlink(translated_path)

            click.secho(f"  ✓ Success: {output_file.name}", fg="green")
            successful += 1

        except Exception as e:
            click.secho(f"  ✗ Failed: {e}", fg="red")
            failed += 1
            failed_files.append(str(rel_path))

            # Cleanup temp files on error
            try:
                if "extracted_path" in locals():
                    os.unlink(extracted_path)
                if "translated_path" in locals():
                    os.unlink(translated_path)
            except Exception:
                pass

        click.echo()  # Empty line between files

    # Summary
    if successful > 0:
        click.secho(f"✓ Success: {successful}/{len(doc_files)}", fg="green")

    if skipped > 0:
        click.secho(f"⊚ Skipped: {skipped}/{len(doc_files)}", fg="yellow")

    if failed > 0:
        click.secho(f"✗ Failed: {failed}/{len(doc_files)}", fg="red")
        click.echo("\nFailed files:")
        for failed_file in failed_files:
            click.echo(f"  - {failed_file}")


if __name__ == "__main__":
    cli()

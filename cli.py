#!/usr/bin/env python3
"""CLI for PPTX slide translator."""

import os
import sys
import tempfile
from pathlib import Path

import click

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src import extractor, reintegrator, translator


@click.group()
@click.version_option(version="1.0.0", prog_name="PPTX Translator")
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
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
def extract(input, output):
    """Extract text from PPTX to JSON."""
    try:
        extractor.extract(input, output)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--target-lang", required=True, help="Target language code (e.g., es, fr, de)")
@click.option("--source-lang", default=None, help="Source language code (optional)")
def translate(input, output, target_lang, source_lang):
    """Translate JSON using Gemini API."""
    try:
        translator.translate(input, output, target_lang, source_lang)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.argument("original", type=click.Path(exists=True))
@click.argument("translated_json", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
def reintegrate(original, translated_json, output):
    """Reintegrate translated text into PPTX."""
    try:
        reintegrator.reintegrate(original, translated_json, output)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


@cli.command("translate-pptx")
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--target-lang", required=True, help="Target language code (e.g., es, fr, de)")
@click.option("--source-lang", default=None, help="Source language code (optional)")
def translate_pptx(input, output, target_lang, source_lang):
    """Translate PPTX file (full pipeline)."""
    try:
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_extract:
            extracted_path = tmp_extract.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_translate:
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
@click.option("--target-lang", required=True, help="Target language code (e.g., es, fr, de)")
@click.option("--source-lang", default=None, help="Source language code (optional)")
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
def translate_dir(input_dir, output_dir, target_lang, source_lang, recursive, skip_existing, overwrite_existing):
    """Translate all PPTX files in a directory.

    This will:
    - Find all .pptx files in the input directory
    - Translate each one to the target language
    - Save translated files to output directory with same filenames
    - Continue processing even if individual files fail
    """
    # Check for conflicting flags
    if skip_existing and overwrite_existing:
        click.secho("✗ Error: Cannot use both --skip and --overwrite together", fg="red", err=True)
        sys.exit(1)

    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all PPTX files
    pptx_files = (
        list(input_path.rglob("*.pptx")) if recursive else list(input_path.glob("*.pptx"))
    )

    if not pptx_files:
        click.secho(f"✗ No PPTX files found in {input_dir}", fg="yellow")
        return

    # Check for existing files if not overwriting or skipping
    if not skip_existing and not overwrite_existing:
        existing_files = []
        for pptx_file in pptx_files:
            rel_path = pptx_file.relative_to(input_path)
            output_file = output_path / rel_path
            if output_file.exists():
                existing_files.append(str(rel_path))

        if existing_files:
            click.secho(f"\n✗ Error: {len(existing_files)} file(s) already exist in output directory:", fg="red")
            for file in existing_files[:10]:  # Show first 10
                click.echo(f"  - {file}")
            if len(existing_files) > 10:
                click.echo(f"  ... and {len(existing_files) - 10} more")
            click.echo("\nOptions:")
            click.echo("  --skip      Skip existing files and translate only new ones")
            click.echo("  --overwrite Overwrite existing files")
            sys.exit(1)

    click.echo(f"Found {len(pptx_files)} PPTX file(s) to translate")
    click.echo(f"Target language: {target_lang}")
    click.echo(f"Output directory: {output_dir}")
    if skip_existing:
        click.echo("Mode: Skip existing files")
    elif overwrite_existing:
        click.echo("Mode: Overwrite existing files")
    click.echo()

    successful = 0
    failed = 0
    skipped = 0
    failed_files = []

    for idx, pptx_file in enumerate(pptx_files, 1):
        # Calculate relative path for subdirectories
        rel_path = pptx_file.relative_to(input_path)
        output_file = output_path / rel_path

        # Check if output file exists and handle based on flags
        if output_file.exists():
            if skip_existing:
                click.echo(f"[{idx}/{len(pptx_files)}] Skipping: {rel_path} (already exists)")
                skipped += 1
                click.echo()
                continue
            elif not overwrite_existing:
                # This shouldn't happen due to earlier check, but just in case
                click.secho(f"[{idx}/{len(pptx_files)}] Error: {rel_path} already exists", fg="red")
                failed += 1
                failed_files.append(str(rel_path))
                click.echo()
                continue

        # Create subdirectories in output if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)

        click.echo(f"[{idx}/{len(pptx_files)}] Processing: {rel_path}")

        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_extract:
                extracted_path = tmp_extract.name

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as tmp_translate:
                translated_path = tmp_translate.name

            # Extract
            extractor.extract(str(pptx_file), extracted_path)

            # Translate
            translator.translate(extracted_path, translated_path, target_lang, source_lang)

            # Reintegrate
            reintegrator.reintegrate(str(pptx_file), translated_path, str(output_file))

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
    click.echo("=" * 50)
    click.secho(f"✓ Successful: {successful}/{len(pptx_files)}", fg="green")

    if skipped > 0:
        click.secho(f"⊘ Skipped: {skipped}/{len(pptx_files)}", fg="yellow")

    if failed > 0:
        click.secho(f"✗ Failed: {failed}/{len(pptx_files)}", fg="red")
        click.echo("\nFailed files:")
        for failed_file in failed_files:
            click.echo(f"  - {failed_file}")


if __name__ == "__main__":
    cli()

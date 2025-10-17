"""Base class for document handlers (extraction + reintegration)."""

import json
from abc import ABC, abstractmethod


class BaseDocumentHandler(ABC):
    """Base class for handling document extraction and reintegration."""

    # ========== Extraction Methods ==========

    @abstractmethod
    def extract_text(self, file_path):
        """Extract text from a document file.

        Args:
            file_path: Path to the document file

        Returns:
            dict: JSON structure with extracted text
        """
        pass

    def save_json(self, data, output_path):
        """Save extracted data to JSON file.

        Args:
            data: Dictionary with extracted data
            output_path: Path to save JSON file
        """
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def extract(self, input_path, output_path):
        """Extract text from document to JSON.

        Args:
            input_path: Path to input document file
            output_path: Path to output JSON file
        """
        data = self.extract_text(input_path)
        self.save_json(data, output_path)
        self.print_extraction_summary(data)

    @abstractmethod
    def print_extraction_summary(self, data):
        """Print extraction summary.

        Args:
            data: Extracted data dictionary
        """
        pass

    # ========== Reintegration Methods ==========

    def load_json(self, json_path):
        """Load translated JSON file.

        Args:
            json_path: Path to JSON file

        Returns:
            dict: Translated data
        """
        with open(json_path, encoding="utf-8") as f:
            return json.load(f)

    @abstractmethod
    def reintegrate_text(self, original_path, translated_data, output_path):
        """Reintegrate translated text into document.

        Args:
            original_path: Path to original document file
            translated_data: Dictionary with translated text
            output_path: Path to save output document file

        Returns:
            int: Number of text elements replaced
        """
        pass

    def reintegrate(self, original_path, translated_json_path, output_path):
        """Reintegrate translated JSON back into document.

        Args:
            original_path: Path to original document file
            translated_json_path: Path to JSON file with translations
            output_path: Path to save output document file
        """
        translated_data = self.load_json(translated_json_path)
        total_replaced = self.reintegrate_text(original_path, translated_data, output_path)
        self.print_reintegration_summary(total_replaced, output_path)

    def print_reintegration_summary(self, total_replaced, output_path):
        """Print reintegration summary.

        Args:
            total_replaced: Number of text elements replaced
            output_path: Output file path
        """
        print(f"✓ Replaced {total_replaced} text elements")
        print(f"✓ Saved to {output_path}")

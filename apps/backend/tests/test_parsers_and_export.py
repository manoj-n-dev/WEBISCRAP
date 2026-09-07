import unittest
import sys
import os
import tempfile
import json
import pandas as pd

# Ensure backend directory is in sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from parsers.document_parser import parse_csv, extract_text_from_file
from agents.exporter import sanitize_cell_value, export_agent, EXPORT_DIR

class TestParsersAndExport(unittest.IsolatedAsyncioTestCase):
    def test_csv_parser(self):
        """Test parsing CSV files into formatted string representation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Product,Price,Rating\nLaptop,1200,4.8\nMouse,25,4.5\n")
            temp_csv = f.name

        try:
            parsed = parse_csv(temp_csv)
            self.assertIn("Laptop", parsed)
            self.assertIn("1200", parsed)
            self.assertIn("Mouse", parsed)
        finally:
            if os.path.exists(temp_csv):
                os.remove(temp_csv)

    def test_txt_parser(self):
        """Test extracting text from plain text and markdown files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test documentation content line 1.\nLine 2.")
            temp_txt = f.name

        try:
            parsed = extract_text_from_file(temp_txt)
            self.assertIn("Test documentation content line 1", parsed)
        finally:
            if os.path.exists(temp_txt):
                os.remove(temp_txt)

    def test_formula_injection_sanitization(self):
        """Test C7: Formula injection protection prevents Excel DDE attacks."""
        # Dangerous formula leading chars: =, +, -, @, \t, \r, \n
        self.assertEqual(sanitize_cell_value("=cmd|' /C calc'!A0"), "'=cmd|' /C calc'!A0")
        self.assertEqual(sanitize_cell_value("+12345"), "'+12345")
        self.assertEqual(sanitize_cell_value("-100"), "'-100")
        self.assertEqual(sanitize_cell_value("@SUM(A1:A10)"), "'@SUM(A1:A10)")
        self.assertEqual(sanitize_cell_value("\tmalicious"), "'\tmalicious")

        # Safe values should remain unaltered
        self.assertEqual(sanitize_cell_value("Standard Product"), "Standard Product")
        self.assertEqual(sanitize_cell_value(99.99), 99.99)
        self.assertEqual(sanitize_cell_value(None), None)

    async def test_exporter_agent_csv_generation(self):
        """Test ExporterAgent generating sanitized CSV."""
        input_data = {
            "cleaned_data": [
                {"Product": "MacBook Pro", "Price": "$1999", "Formula": "=1+1"},
                {"Product": "ThinkPad X1", "Price": "$1499", "Formula": "@DDE"}
            ],
            "export_requested": "csv",
            "owner_id": "test_user_123"
        }

        output = await export_agent.run(input_data, session_id="test_export_sess")
        export_url = output.get("export_url")
        self.assertIsNotNone(export_url)
        self.assertTrue(export_url.startswith("/api/export/download/"))

        # Verify the generated file exists on disk
        filename = export_url.replace("/api/export/download/", "")
        file_path = os.path.join(EXPORT_DIR, filename)
        self.assertTrue(os.path.exists(file_path))

        # Check content and formula escaping
        content = open(file_path, "r", encoding="utf-8").read()
        self.assertIn("MacBook Pro", content)
        self.assertIn("ThinkPad X1", content)
        self.assertIn("'=1+1", content) # Sanitized!

        # Clean up
        os.remove(file_path)

    async def test_exporter_agent_json_generation(self):
        """Test ExporterAgent generating JSON export."""
        input_data = {
            "cleaned_data": [
                {"Name": "Item A", "Score": 95},
                {"Name": "Item B", "Score": 88}
            ],
            "export_requested": "json",
            "owner_id": "test_user_123"
        }

        output = await export_agent.run(input_data, session_id="test_json_export")
        export_url = output.get("export_url")
        self.assertIsNotNone(export_url)

        filename = export_url.replace("/api/export/download/", "")
        file_path = os.path.join(EXPORT_DIR, filename)
        self.assertTrue(os.path.exists(file_path))

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["Name"], "Item A")

        # Clean up
        os.remove(file_path)

    async def test_exporter_agent_excel_generation(self):
        """Test ExporterAgent generating Excel (.xlsx) export."""
        input_data = {
            "cleaned_data": [
                {"Column1": "Data 1", "Column2": 100},
                {"Column1": "Data 2", "Column2": 200}
            ],
            "export_requested": "excel",
            "owner_id": "test_user_123"
        }

        output = await export_agent.run(input_data, session_id="test_excel_export")
        export_url = output.get("export_url")
        self.assertIsNotNone(export_url)
        self.assertTrue(export_url.endswith(".xlsx"))

        filename = export_url.replace("/api/export/download/", "")
        file_path = os.path.join(EXPORT_DIR, filename)
        self.assertTrue(os.path.exists(file_path))

        # Clean up
        os.remove(file_path)

if __name__ == "__main__":
    unittest.main()

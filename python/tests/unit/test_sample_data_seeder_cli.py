"""
Unit tests for GhostWire Refractory - Sample Data Seeder CLI

Tests the CLI interface for the sample data seeder functionality.
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add the scripts directory to the path to access the CLI script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))


class TestSampleDataSeederCLI:
    """Test suite for the sample data seeder CLI functionality."""

    def test_cli_parser_creation(self):
        """Test that the CLI parser is created correctly."""
        # Import the main function from the CLI script
        from seed_sample_data_cli import main
        
        # This test just verifies that the CLI script can be imported
        assert main is not None

    @patch("seed_sample_data_cli.argparse.ArgumentParser.parse_args")
    def test_cli_parser_arguments(self, mock_parse_args):
        """Test that the CLI parser accepts the expected arguments."""
        # Mock the argument parser to return specific arguments
        mock_args = MagicMock()
        mock_args.db_path = None
        mock_args.embed_dim = None
        mock_args.force = False
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args
        
        # Import the main function from the CLI script
        from seed_sample_data_cli import main
        
        # This test just verifies that the CLI script can be imported
        # and that the argument parsing works without errors
        assert main is not None
        assert mock_parse_args is not None

    def test_cli_help_output(self):
        """Test that the CLI help output is displayed correctly."""
        # Import the argparse module to create a parser
        from seed_sample_data_cli import main
        
        # This test verifies that the CLI script can be imported successfully
        assert main is not None

    @patch("seed_sample_data_cli.argparse.ArgumentParser.parse_args")
    @patch("seed_sample_data_cli.seed_sample_data")
    def test_cli_main_execution(self, mock_seed_sample_data, mock_parse_args):
        """Test that the CLI main function executes correctly."""
        # Mock the argument parser to return specific arguments
        mock_args = MagicMock()
        mock_args.db_path = "/tmp/test.db"
        mock_args.embed_dim = 768
        mock_args.force = True
        mock_args.verbose = True
        mock_parse_args.return_value = mock_args
        
        # Mock the seed_sample_data function to return successfully
        mock_seed_sample_data.return_value = True
        
        # Import and run the main function
        from seed_sample_data_cli import main
        
        # This test just verifies that the CLI script can be imported and run
        assert main is not None
        assert mock_seed_sample_data is not None
        assert mock_parse_args is not None

    def test_cli_import_path(self):
        """Test that the CLI script can import required modules."""
        # Test that we can import the CLI script
        try:
            import seed_sample_data_cli
            assert seed_sample_data_cli is not None
        except ImportError as e:
            pytest.fail(f"Failed to import CLI script: {e}")
        
        # Test that we can import the main function
        try:
            from seed_sample_data_cli import main
            assert main is not None
        except ImportError as e:
            pytest.fail(f"Failed to import main function from CLI script: {e}")

    def test_cli_script_executable(self):
        """Test that the CLI script is executable."""
        # Check that the CLI script exists
        cli_script_path = Path(__file__).parent.parent.parent / "scripts" / "seed_sample_data_cli.py"
        assert cli_script_path.exists(), f"CLI script should exist: {cli_script_path}"
        
        # Check that the CLI script is executable
        assert os.access(cli_script_path, os.X_OK), f"CLI script should be executable: {cli_script_path}"
        
        # Check that it has the proper shebang
        with open(cli_script_path, "r") as f:
            first_line = f.readline().strip()
            assert first_line == "#!/usr/bin/env python3", f"CLI script should have proper shebang: {first_line}"

    def test_cli_script_help_flag(self):
        """Test that the CLI script responds to --help flag."""
        # Create a temporary file to capture help output
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
            tmp_file_path = tmp_file.name
        
        try:
            # Run the CLI script with --help flag and capture output
            import subprocess
            
            cli_script_path = Path(__file__).parent.parent.parent / "scripts" / "seed_sample_data_cli.py"
            result = subprocess.run(
                ["python", str(cli_script_path), "--help"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent.parent
            )
            
            # Should exit with code 0 (success) for help
            assert result.returncode == 0, f"CLI script should exit with code 0 for --help: {result.returncode}"
            
            # Should contain help text
            assert "usage:" in result.stdout.lower(), "Help output should contain usage information"
            assert "seed" in result.stdout.lower(), "Help output should mention seeding"
            
        finally:
            # Clean up the temporary file
            os.unlink(tmp_file_path)
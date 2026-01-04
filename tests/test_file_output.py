"""Tests for file output handling."""

import pytest
from pathlib import Path
from scraper.file_output import FileOutput


class TestFileOutput:
    """Tests for FileOutput class."""

    def test_write_toml_creates_file(self, temp_dir):
        """Test that TOML is written to file."""
        content = '[test]\nkey = "value"\n'
        output_path = temp_dir / "output.toml"

        result = FileOutput.write_toml(content, str(output_path))

        assert Path(result).exists()
        assert result == str(output_path.resolve())

    def test_write_toml_creates_directory(self, temp_dir):
        """Test that output directory is created if missing."""
        content = '[test]\nkey = "value"\n'
        nested_path = temp_dir / "subdir" / "output.toml"

        FileOutput.write_toml(content, str(nested_path))

        assert nested_path.exists()
        assert nested_path.parent.exists()

    def test_write_toml_overwrites_existing(self, temp_dir):
        """Test that existing file is overwritten."""
        output_path = temp_dir / "output.toml"
        output_path.write_text("old content")

        new_content = '[new]\nkey = "new value"\n'
        FileOutput.write_toml(new_content, str(output_path))

        assert output_path.read_text() == new_content

    def test_write_toml_returns_absolute_path(self, temp_dir):
        """Test that returned path is absolute."""
        content = '[test]\nkey = "value"\n'
        output_path = temp_dir / "output.toml"

        result = FileOutput.write_toml(content, str(output_path))

        assert Path(result).is_absolute()

    def test_generate_filename_from_site_name(self):
        """Test filename generation from site name."""
        filename = FileOutput.generate_filename("Example Fablab")
        assert "example-fablab" in filename
        assert filename.endswith(".toml")

    def test_generate_filename_with_timestamp(self):
        """Test filename generation with timestamp."""
        filename = FileOutput.generate_filename("Example Site", "2026-01-04T10:00:00Z")
        assert "2026-01-04" in filename
        assert "example-site" in filename

    def test_generate_filename_sanitizes_special_chars(self):
        """Test that special characters are sanitized."""
        filename = FileOutput.generate_filename("Lab/Site Name")
        # Should not have slashes or spaces
        assert "/" not in filename
        assert " " not in filename
        assert "-" in filename  # Should have dashes

    def test_verify_file_exists(self, temp_dir):
        """Test file verification for existing file."""
        output_path = temp_dir / "test.toml"
        output_path.write_text('[test]\nkey = "value"\n')

        assert FileOutput.verify_file(str(output_path)) is True

    def test_verify_file_not_found(self, temp_dir):
        """Test verification fails for non-existent file."""
        output_path = temp_dir / "nonexistent.toml"

        with pytest.raises(IOError, match="not found"):
            FileOutput.verify_file(str(output_path))

    def test_verify_file_empty_file(self, temp_dir):
        """Test verification fails for empty file."""
        output_path = temp_dir / "empty.toml"
        output_path.write_text("")

        with pytest.raises(IOError, match="empty"):
            FileOutput.verify_file(str(output_path))

    def test_verify_file_is_directory(self, temp_dir):
        """Test verification fails if path is directory."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()

        with pytest.raises(IOError, match="not a file"):
            FileOutput.verify_file(str(subdir))

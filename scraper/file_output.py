"""File I/O operations for output handling."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class FileOutput:
    """Handles writing and managing output files."""

    @staticmethod
    def write_toml(toml_content: str, output_path: str) -> str:
        """
        Write TOML content to file.

        Creates output directory if it doesn't exist.

        Args:
            toml_content: TOML-formatted string content
            output_path: Path to output file

        Returns:
            Path to written file

        Raises:
            IOError: If file writing fails
        """
        path = Path(output_path)

        # Create parent directory if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Output directory created: {path.parent}")

        try:
            with open(path, "w") as f:
                f.write(toml_content)
            logger.info(f"TOML output written to {output_path}")
            return str(path.resolve())
        except IOError as e:
            msg = f"Failed to write output file: {e}"
            logger.error(msg)
            raise IOError(msg) from e

    @staticmethod
    def generate_filename(site_name: str, timestamp: str = None) -> str:
        """
        Generate output filename from site name and timestamp.

        Args:
            site_name: Name of the site
            timestamp: Optional ISO format timestamp

        Returns:
            Suggested filename
        """
        # Sanitize site name
        safe_name = site_name.lower().replace(" ", "-").replace("/", "-")

        if timestamp:
            # Extract date part from ISO timestamp (YYYY-MM-DD)
            date_part = timestamp.split("T")[0] if "T" in timestamp else timestamp
            return f"{date_part}_{safe_name}.toml"
        else:
            return f"{safe_name}.toml"

    @staticmethod
    def verify_file(file_path: str) -> bool:
        """
        Verify that file was written correctly.

        Args:
            file_path: Path to file to verify

        Returns:
            True if file exists and is readable

        Raises:
            IOError: If file cannot be read
        """
        path = Path(file_path)

        try:
            if not path.exists():
                raise IOError(f"File not found: {file_path}")

            if not path.is_file():
                raise IOError(f"Path is not a file: {file_path}")

            # Try to read file
            with open(path, "r") as f:
                content = f.read()

            if not content:
                raise IOError(f"File is empty: {file_path}")

            logger.debug(f"File verified: {file_path}")
            return True

        except (IOError, OSError) as e:
            logger.error(f"File verification failed: {e}")
            raise

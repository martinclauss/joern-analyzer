import json
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger


class FileHandler:
    @staticmethod
    def read_json(file_path: Path) -> List[Dict[str, Any]]:
        """Read and parse a JSON file."""
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading JSON file {file_path}: {str(e)}")
            return []

    @staticmethod
    def write_json(data: Any, file_path: Path) -> bool:
        """Write data to a JSON file."""
        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error writing JSON file {file_path}: {str(e)}")
            return False

    @staticmethod
    def read_text(file_path: Path) -> str:
        """Read text content from a file."""
        try:
            with open(file_path, "r") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {str(e)}")
            return ""

    @staticmethod
    def write_text(content: str, file_path: Path) -> bool:
        """Write text content to a file."""
        try:
            with open(file_path, "w") as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Error writing text file {file_path}: {str(e)}")
            return False

    @staticmethod
    def find_source_files(directory: Path, extensions: set) -> List[Path]:
        """Find all source files with given extensions in a directory."""
        source_files = []
        for file_path in directory.glob("**/*"):
            if file_path.is_file() and file_path.suffix in extensions:
                source_files.append(file_path)
        return source_files

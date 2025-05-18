#!/usr/bin/env python3

"""
Simple REST Client for Code Analysis API

This module provides a client interface for interacting with a code analysis API.
It handles uploading code for analysis, retrieving analysis results, and displaying
the results in a readable format. The module supports zipping code directories,
uploading them to the API, and processing the returned analysis data.

The API is expected to be running at http://localhost:3003 and provides endpoints
for code upload and analysis retrieval.

Example:
    ```python
    # Check if API is running
    if is_api_running():
        # Upload code for analysis
        code_id = upload_code(Path("path/to/code.zip"))
        if code_id:
            # Get and display results
            results = get_analysis_results(code_id)
            display_results(results)
    ```
"""

import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict

import requests
from loguru import logger

# API configuration
API_BASE_URL = "http://localhost:3003"


def create_zip_from_directory(source_dir: Path, zip_path: Path) -> bool:
    """Create a zip file from a directory.

    This function recursively zips all files in the source directory and its
    subdirectories, maintaining the directory structure in the zip file.

    Args:
        source_dir (Path): Source directory to zip. Must be a valid directory path.
        zip_path (Path): Path where to save the zip file. Should end with .zip extension.

    Returns:
        bool: True if zip creation was successful, False otherwise.

    Example:
        ```python
        success = create_zip_from_directory(
            Path("src"),
            Path("output.zip")
        )
        ```
    """
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.glob("**/*"):
                if file_path.is_file():
                    # Use relative path in zip
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)
        return True
    except Exception as e:
        logger.error(f"Error creating zip file: {str(e)}")
        return False


def upload_code(zip_path: Path) -> str:
    """Upload code to the API for analysis.

    This function sends a zip file containing code to the API for analysis.
    The API will process the code and return a unique code ID that can be used
    to retrieve the analysis results later.

    Args:
        zip_path (Path): Path to the zip file containing the code to analyze.
            Must be a valid zip file path.

    Returns:
        str: Code ID if upload was successful, empty string otherwise.
            The code ID is required for retrieving analysis results.

    Example:
        ```python
        code_id = upload_code(Path("code.zip"))
        if code_id:
            print(f"Code uploaded with ID: {code_id}")
        ```
    """
    try:
        with open(zip_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{API_BASE_URL}/upload_code", files=files)

        if response.status_code == 200:
            result = response.json()
            logger.info(f"Code uploaded successfully. Code ID: {result['code_id']}")
            return result["code_id"]
        else:
            logger.error(f"Upload failed: {response.text}")
            return ""

    except Exception as e:
        logger.error(f"Error uploading code: {str(e)}")
        return ""


def get_analysis_results(code_id: str) -> Dict[str, Any]:
    """Get analysis results from the API.

    This function retrieves the analysis results for previously uploaded code
    using the provided code ID. The results include function information,
    call graph data, and a tree representation of the call graph.

    Args:
        code_id (str): ID of the uploaded code, obtained from upload_code().
            Must be a valid code ID returned by the API.

    Returns:
        Dict[str, Any]: Dictionary containing analysis results with the following keys:
            - functions: List of all functions found in the code
            - cleaned_functions: List of functions after cleaning
            - call_graph: List of all function calls
            - cleaned_call_graph: List of calls after cleaning
            - call_graph_tree: Tree representation of the call graph

    Example:
        ```python
        results = get_analysis_results("abc123")
        if results:
            print(f"Found {len(results['functions'])} functions")
        ```
    """
    try:
        response = requests.get(f"{API_BASE_URL}/call_graph/{code_id}")

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get results: {response.text}")
            return {}

    except Exception as e:
        logger.error(f"Error getting results: {str(e)}")
        return {}


def display_results(results: Dict[str, Any]) -> None:
    """Display analysis results in a readable format.

    This function formats and prints the analysis results in a structured way,
    showing function counts, call graph information, and a tree representation
    of the call graph.

    Args:
        results (Dict[str, Any]): Dictionary containing analysis results from
            get_analysis_results(). Should contain the expected keys for
            functions, call graph, and tree data.

    Example:
        ```python
        results = get_analysis_results("abc123")
        display_results(results)
        ```
    """
    if not results:
        logger.error("No results to display")
        return

    # Display function information
    logger.info("\n=== Function Information ===")
    logger.info(f"Total functions: {len(results.get('functions', []))}")
    logger.info(f"Cleaned functions: {len(results.get('cleaned_functions', []))}")

    # Display call graph information
    logger.info("\n=== Call Graph Information ===")
    logger.info(f"Total calls: {len(results.get('call_graph', []))}")
    logger.info(f"Cleaned calls: {len(results.get('cleaned_call_graph', []))}")

    # Display call graph tree
    logger.info("\n=== Call Graph Tree ===")
    for line in results.get("call_graph_tree", []):
        logger.info(line)


def is_api_running() -> bool:
    """Check if the API is running and accessible.

    This function attempts to connect to the API server to verify it is
    running and accessible. It uses a 5-second timeout to avoid hanging
    if the server is not responding.

    Returns:
        bool: True if API is running and accessible, False otherwise.

    Example:
        ```python
        if is_api_running():
            print("API is available")
        else:
            print("API is not running")
        ```
    """
    try:
        _ = requests.get(API_BASE_URL, timeout=5)
        return True
    except requests.RequestException as e:
        logger.error(f"API is not running: {str(e)}")
        return False


def main() -> None:
    """Main function to demonstrate API usage.

    This function demonstrates the complete workflow of:
    1. Checking API availability
    2. Creating a zip file from test code
    3. Uploading the code for analysis
    4. Retrieving and displaying the results

    The function uses a temporary directory for the zip file and cleans up
    after execution.

    Example:
        ```python
        if __name__ == '__main__':
            main()
        ```
    """
    # Check if API is running first
    if not is_api_running():
        logger.error("API is not running. Please start the API server first.")
        return

    # Create a temporary directory for the zip file
    temp_dir = Path.cwd() / "temp"
    temp_dir.mkdir(exist_ok=True)

    try:
        # Path to the test code
        test_code_dir = Path.cwd() / "test_code" / "more_complex"
        if not test_code_dir.exists():
            logger.error(f"Test code directory not found: {test_code_dir}")
            return

        # Create zip file
        zip_path = temp_dir / "test_code.zip"
        if not create_zip_from_directory(test_code_dir, zip_path):
            return

        # Upload code
        code_id = upload_code(zip_path)
        if not code_id:
            return

        # Get and display results
        results = get_analysis_results(code_id)
        display_results(results)

    finally:
        # Clean up
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()

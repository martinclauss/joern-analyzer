#!/usr/bin/env python3

import hashlib
import shutil
import uuid
import zipfile
from pathlib import Path

import click
from flask import Flask, jsonify, request, Response
from loguru import logger

from joern_analyzer import JoernAnalyzer
from results_processor import ResultsProcessor

app = Flask(__name__)

# Create code and results directories if they don't exist
CODE_DIR = Path.cwd() / "code"
RESULTS_DIR = Path.cwd() / "results"
CODE_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)


def calculate_zip_hash(zip_path: Path) -> str:
    """Calculate SHA-512 hash of a zip file."""
    sha512_hash = hashlib.sha512()
    with open(zip_path, "rb") as f:
        # Read the file in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha512_hash.update(byte_block)
    return sha512_hash.hexdigest()


@app.route("/upload_code", methods=["POST"])
def upload_code() -> tuple[Response, int]:
    """Handle code upload via zip file.

    This endpoint accepts a zip file containing C/C++ source code, extracts it,
    and prepares it for analysis. The code is identified by a SHA-512 hash of
    the zip file contents.

    Request:
        - Method: POST
        - Content-Type: multipart/form-data
        - Body: Form data with 'file' field containing a zip file

    Returns:
        - 200: Success response with code_id
        - 400: Bad request (no file, empty file, or non-zip file)
        - 500: Server error during processing

    The uploaded code is stored in the CODE_DIR directory, with each upload
    getting its own subdirectory named by the hash of the zip contents.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith(".zip"):
        return jsonify({"error": "File must be a zip file"}), 400

    try:
        # Create a temporary file for the zip
        temp_zip = CODE_DIR / f"temp_{uuid.uuid4()}.zip"
        file.save(temp_zip)

        # Calculate hash of the zip file
        code_id = calculate_zip_hash(temp_zip)
        target_dir = CODE_DIR / code_id
        results_dir = RESULTS_DIR / code_id

        # Only extract if directory doesn't exist
        if not target_dir.exists():
            target_dir.mkdir(exist_ok=True)
            with zipfile.ZipFile(temp_zip, "r") as zip_ref:
                zip_ref.extractall(target_dir)

        # Create results directory if it doesn't exist
        results_dir.mkdir(exist_ok=True)

        # Clean up temporary zip file
        temp_zip.unlink()

        return jsonify({"message": "Code uploaded successfully", "code_id": code_id}), 200

    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        # Clean up on error
        if "temp_zip" in locals() and temp_zip.exists():
            temp_zip.unlink()
        if "target_dir" in locals() and target_dir.exists() and not any(target_dir.iterdir()):
            shutil.rmtree(target_dir)
        if "results_dir" in locals() and results_dir.exists() and not any(results_dir.iterdir()):
            shutil.rmtree(results_dir)
        return jsonify({"error": str(e)}), 500


@app.route("/call_graph/<code_id>", methods=["GET"])
def get_call_graph(code_id: str) -> tuple[Response, int]:
    """Analyze code and return call graph results.

    This endpoint triggers the analysis of previously uploaded code and returns
    the call graph and function information. The analysis is performed using
    the Joern static analysis tool.

    Args:
        code_id: The unique identifier of the uploaded code (SHA-512 hash)

    Returns:
        - 200: Success response with analysis results
        - 404: Code ID not found
        - 500: Server error during analysis

    The response includes:
        - functions: Raw function data
        - call_graph: Raw call graph data
        - cleaned_functions: Cleaned function data
        - cleaned_call_graph: Cleaned call graph data
        - call_graph_tree: Formatted call graph tree
    """
    code_path = CODE_DIR / code_id
    results_path = RESULTS_DIR / code_id

    logger.debug(f"API: code_path={code_path}, results_path={results_path}")

    if not code_path.exists():
        logger.error(f"API: Code path does not exist for code_id={code_id}")
        return jsonify({"error": "Code ID not found"}), 404

    try:
        # Initialize and run analyzer
        analyzer = JoernAnalyzer()
        try:
            analyzer.analyze(code_path, results_path)
        except RuntimeError as e:
            logger.error(f"API: Analyzer runtime error: {e}")
            return jsonify({"error": str(e)}), 500

        logger.debug(
            f"API: analyzer.functions_info (len={len(analyzer.functions_info)}) = {analyzer.functions_info[:2] if analyzer.functions_info else analyzer.functions_info}"
        )
        logger.debug(
            f"API: analyzer.call_graph (len={len(analyzer.call_graph)}) = {analyzer.call_graph[:2] if analyzer.call_graph else analyzer.call_graph}"
        )

        # Check result files directly
        functions_file = results_path / "functions.json"
        callgraph_file = results_path / "call_graph.json"
        logger.debug(
            f"API: functions_file exists={functions_file.exists()} size={functions_file.stat().st_size if functions_file.exists() else 'N/A'}"
        )
        logger.debug(
            f"API: callgraph_file exists={callgraph_file.exists()} size={callgraph_file.stat().st_size if callgraph_file.exists() else 'N/A'}"
        )
        if functions_file.exists() and functions_file.stat().st_size > 0:
            with open(functions_file) as f:
                try:
                    functions_data = f.read(500)
                    logger.debug(f"API: functions_file first 500 chars: {functions_data}")
                except Exception as e:
                    logger.error(f"API: Error reading functions_file: {e}")
        if callgraph_file.exists() and callgraph_file.stat().st_size > 0:
            with open(callgraph_file) as f:
                try:
                    callgraph_data = f.read(500)
                    logger.debug(f"API: callgraph_file first 500 chars: {callgraph_data}")
                except Exception as e:
                    logger.error(f"API: Error reading callgraph_file: {e}")

        # Get results
        if not analyzer.functions_info or not analyzer.call_graph:
            logger.error("API: No analysis results available in analyzer attributes after analyze()")
            if not functions_file.exists() or not callgraph_file.exists():
                logger.error("API: Analysis result files not found on disk")
                return jsonify({"error": "Analysis results not found"}), 500
            if functions_file.stat().st_size == 0 or callgraph_file.stat().st_size == 0:
                logger.error("API: Analysis result files are empty on disk")
                return jsonify({"error": "Analysis results are empty"}), 500

        # Process results
        processor = ResultsProcessor(results_path)
        results = processor.get_all_results(analyzer.functions_info or [], analyzer.call_graph or [])
        logger.debug(f"API: Returning results with keys: {list(results.keys())}")

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"API: Error analyzing code: {str(e)}")
        return jsonify({"error": str(e)}), 500


@click.command()
@click.option("--port", default=3003, help="Port to run the server on")
@click.option("--debug", is_flag=True, default=False, help="Enable debug mode")
@click.option("--host", default="127.0.0.1", help="Host to bind the server to")
def main(port: int, debug: bool, host: str) -> None:
    """Run the Flask server."""
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()

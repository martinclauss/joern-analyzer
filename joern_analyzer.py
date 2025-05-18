#! /usr/bin/env python3

"""
Joern Code Analyzer

This module provides functionality to analyze C/C++ code using the Joern static analysis tool.
It performs static code analysis to generate a Code Property Graph (CPG) and extracts
function information and call graphs from the analyzed code.

The analyzer runs Joern in a Docker container to ensure consistent analysis environment
and handles the complete analysis workflow including:
- Starting/stopping the Joern server
- Importing source code
- Running analysis scripts
- Processing and storing results

Dependencies:
    - Docker (for running Joern)
    - Python 3.x
    - Required Python packages: click, loguru
"""

import hashlib
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, cast
import json

import click
from loguru import logger

from results_processor import ResultsProcessor
from settings import ANALYSIS_SETTINGS, C_CPP_EXTENSIONS, CONTAINER_PATHS, DOCKER_SETTINGS, JAVA_OPTS
from utils.docker_manager import DockerManager
from utils.file_handler import FileHandler


class JoernAnalyzer:
    """
    A standalone class for analyzing C/C++ code using Joern static analysis tool.

    This analyzer performs static code analysis on C/C++ source code to generate
    function information and call graphs. It manages the complete analysis workflow
    including Docker container management, code import, analysis execution, and
    results processing.

    Attributes:
        code_path (Optional[Path]): Path to the source code to be analyzed
        results_path (Optional[Path]): Path where analysis results will be stored
        docker_manager (DockerManager): Manager for Docker container operations
        file_handler (FileHandler): Handler for file operations
        results_processor (Optional[ResultsProcessor]): Processor for analysis results
        functions_info (List[Dict[str, Any]]): List of function information dictionaries
        call_graph (List[Dict[str, Any]]): List of call graph entries
    """

    def __init__(self) -> None:
        """
        Initialize the Joern analyzer.

        Sets up the Docker manager with Joern image and initializes file handling
        components. The analyzer is ready to perform code analysis after initialization.
        """
        self.code_path: Optional[Path] = None
        self.results_path: Optional[Path] = None
        docker_settings = cast(Dict[str, Dict[str, str]], DOCKER_SETTINGS)
        self.docker_manager = DockerManager(
            image=docker_settings["joern"]["image"], platform=docker_settings["joern"]["platform"]
        )
        self.file_handler = FileHandler()
        self.results_processor: Optional[ResultsProcessor] = None
        self.functions_info: List[Dict[str, Any]] = []
        self.call_graph: List[Dict[str, Any]] = []

    def analyze(self, path: Path, base_path: Optional[Path] = None) -> None:
        """
        Analyze C/C++ code at the given path.

        This method orchestrates the complete analysis workflow:
        1. Starts the Joern server
        2. Sets up the results directory
        3. Imports the code and generates CPG
        4. Runs the analysis
        5. Processes and stores the results

        Args:
            path (Path): Path to the C/C++ source code to analyze
            base_path (Optional[Path]): Optional base path for relative path calculations.
                If not provided, a results directory will be created based on the code path hash.

        Raises:
            RuntimeError: If any step in the analysis workflow fails
        """
        try:
            if base_path is None:
                code_path_abs = Path(path).resolve()
                code_path_abs_hash = hashlib.sha512(str(code_path_abs).encode()).hexdigest()
                base_path = Path.cwd() / "results" / code_path_abs_hash
                base_path.mkdir(parents=True, exist_ok=True)

            logger.info(f"Analyzing C/C++ code at: {path}")
            logger.info(f"Storing results at: {base_path}")

            self.code_path = path
            self.results_path = base_path
            self.results_processor = ResultsProcessor(self.results_path)

            if not self._start_server():
                raise RuntimeError("Failed to start Joern server")

            if not self._setup_results_directory():
                raise RuntimeError("Failed to setup results directory")

            if not self._import_code():
                raise RuntimeError("Failed to import code and generate CPG")

            if not self._run_analysis():
                raise RuntimeError("Failed to run analysis")

            self._process_results()

        finally:
            self._stop_server()

    def _start_server(self) -> bool:
        """
        Start the Joern server in a Docker container.

        Sets up the Docker container with necessary volume mounts and environment
        variables for running Joern analysis.

        Returns:
            bool: True if server started successfully, False otherwise
        """
        logger.info("Starting Joern server...")

        joern_scripts_path = Path(__file__).parent / "joern_scripts"
        container_paths = cast(Dict[str, str], CONTAINER_PATHS)

        # Create volumes dictionary with proper typing
        volumes: Dict[str, Dict[str, str]] = {}
        if self.code_path:
            volumes[str(self.code_path)] = {"bind": container_paths["app"], "mode": "ro"}
        if self.results_path:
            volumes[str(self.results_path)] = {"bind": container_paths["results"], "mode": "rw"}
        volumes[str(joern_scripts_path)] = {"bind": container_paths["scripts"], "mode": "ro"}

        success = self.docker_manager.start_container(
            image=self.docker_manager.image,
            command=["tail", "-f", "/dev/null"],
            volumes=volumes,
            environment={"JAVA_OPTS": " ".join(JAVA_OPTS), "JOERN_LOG_LEVEL": "debug"},
            working_dir=container_paths["results"],
        )

        if not success:
            logger.error("Failed to start Joern server")
            return False

        return True

    def _setup_results_directory(self) -> bool:
        """
        Set up the results directory in the container.

        Creates and configures the results directory with appropriate permissions
        for storing analysis outputs.

        Returns:
            bool: True if directory setup was successful, False otherwise
        """
        container_paths = cast(Dict[str, str], CONTAINER_PATHS)
        results_path = container_paths["results"]

        # Create commands with proper typing
        commands: List[List[str]] = [["mkdir", "-p", results_path], ["chmod", "777", results_path]]

        for cmd in commands:
            success, stdout, stderr = self.docker_manager.execute_command(cmd)
            if not success:
                logger.error(f"Failed to setup results directory: {stderr}")
                return False

        return True

    def _stop_server(self) -> None:
        """
        Stop the Joern server and clean up resources.

        Gracefully stops the Docker container and releases associated resources.
        """
        logger.info("Stopping Joern server...")
        self.docker_manager.stop_container()

    def _import_code(self) -> bool:
        """
        Import code into Joern and generate Code Property Graph (CPG).

        Scans the source directory for C/C++ files and uses Joern's c2cpg tool
        to generate the initial CPG representation of the code.

        Returns:
            bool: True if code import was successful, False otherwise
        """
        logger.info("Importing code into Joern...")

        if self.code_path is None:
            logger.error("Code path is not set")
            return False

        source_files = self.file_handler.find_source_files(self.code_path, C_CPP_EXTENSIONS)
        if not source_files:
            logger.error(f"No C/C++ source files found in {self.code_path}")
            return False

        logger.info(f"Found {len(source_files)} C/C++ source files")

        container_paths = cast(Dict[str, str], CONTAINER_PATHS)
        app_path = container_paths["app"]
        results_path = container_paths["results"]

        # Create command with proper typing
        command: List[str] = [
            "/opt/joern/joern-cli/c2cpg.sh",
            *[f"-J{opt}" for opt in JAVA_OPTS],
            app_path,
            "--output",
            f"{results_path}/cpg.bin",
        ]

        success, stdout, stderr = self.docker_manager.execute_command(
            command,
            timeout=ANALYSIS_SETTINGS["timeout"]["command_execution"],
        )

        if not success:
            logger.error(f"Failed to import code: {stderr}")
            return False

        return True

    def _run_analysis(self) -> bool:
        """
        Run the Joern analysis script on the imported code.

        Executes the analysis script to extract function information and
        generate the call graph from the CPG.

        Returns:
            bool: True if analysis completed successfully, False otherwise
        """
        logger.debug("Running analysis script...")

        container_paths = cast(Dict[str, str], CONTAINER_PATHS)
        results_path = container_paths["results"]
        scripts_path = container_paths["scripts"]

        # Create command as a list of strings
        command: List[str] = [
            "sh",
            "-c",
            f"cd {results_path} && /opt/joern/joern-cli/joern --script {scripts_path}/analysis.sc",
        ]

        success, stdout, stderr = self.docker_manager.execute_command(
            command,
            timeout=ANALYSIS_SETTINGS["timeout"]["command_execution"],
        )

        if not success:
            logger.error(f"Failed to run analysis script: {stderr}")
            return False

        return True

    def _process_results(self) -> None:
        """
        Process and save the analysis results.

        Reads the generated function information and call graph files,
        processes them through the results processor, and saves the
        formatted results.

        The processed results include:
        - Function information (signatures, locations, etc.)
        - Call graph representation
        - Cleaned and formatted analysis data
        """
        if not self.results_processor or not self.results_path:
            logger.error("Results processor or path not initialized")
            return

        try:
            # Read and process function information
            functions_file = self.results_path / "functions.json"
            if functions_file.exists() and functions_file.stat().st_size > 0:
                with open(functions_file) as f:
                    functions_data = json.load(f)
                    if isinstance(functions_data, list):
                        self.functions_info = functions_data
                    elif isinstance(functions_data, dict):
                        self.functions_info = [functions_data]

            # Read and process call graph
            callgraph_file = self.results_path / "call_graph.json"
            if callgraph_file.exists() and callgraph_file.stat().st_size > 0:
                with open(callgraph_file) as f:
                    callgraph_data = json.load(f)
                    if isinstance(callgraph_data, list):
                        self.call_graph = callgraph_data
                    elif isinstance(callgraph_data, dict):
                        self.call_graph = [callgraph_data]

            # Save raw results
            self.results_processor.save_raw_results(self.functions_info, self.call_graph)

            # Clean and format results
            self.results_processor.clean_and_format_results()

        except Exception as e:
            logger.exception(f"Error processing results: {str(e)}")
            raise RuntimeError(f"Failed to process results: {str(e)}")


@click.command()
@click.argument("code_path", type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True))
def main(code_path: str) -> None:
    """
    Analyze C/C++ code using Joern and generate function information and call graph.

    This is the main entry point for the analyzer. It sets up the analysis environment,
    creates a unique results directory based on the code path hash, and runs the
    complete analysis workflow.

    Args:
        code_path (str): Path to the directory containing C/C++ source code to analyze

    The results are stored in a directory structure:
    ./results/<code_path_hash>/
        - functions.json: Function information
        - call_graph.json: Call graph representation
        - processed_results/: Cleaned and formatted analysis results
    """
    try:
        code_path_abs = Path(code_path).resolve()
        code_path_abs_hash = hashlib.sha512(str(code_path_abs).encode()).hexdigest()

        results_dir = Path.cwd() / "results" / code_path_abs_hash
        results_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Code path: {code_path_abs}")
        logger.info(f"Results directory: {results_dir}")

        analyzer = JoernAnalyzer()
        analyzer.analyze(code_path_abs, results_dir)

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

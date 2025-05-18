"""Results Processor Module

This module provides functionality for processing, cleaning, and formatting code analysis results.
It handles function information and call graph data, providing various output formats and cleaning
operations to make the analysis results more usable and readable.

The module supports:
- Cleaning and filtering function data
- Processing call graphs
- Converting call graphs to tree structures
- Saving results in various formats (JSON and text)
"""

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Set

from loguru import logger

from settings import SYSTEM_FUNCTIONS
from utils.file_handler import FileHandler


class ResultPaths(NamedTuple):
    """Container for result file paths."""

    functions: Path
    functions_clean: Path
    call_graph: Path
    call_graph_clean: Path
    call_graph_tree: Path


class ResultsProcessor:
    """A class for processing and formatting code analysis results.

    This class handles the processing of function information and call graph data,
    providing methods to clean, format, and save the results in various formats.

    Attributes:
        results_path (Path): Path to the directory where results will be saved
        file_handler (FileHandler): Instance of FileHandler for file operations
    """

    def __init__(self, results_path: Path):
        """Initialize the ResultsProcessor.

        Args:
            results_path (Path): Path to the directory where results will be saved
        """
        self.results_path = results_path
        self.file_handler = FileHandler()

    def _get_result_paths(self) -> ResultPaths:
        """Get all result file paths.

        Returns:
            ResultPaths: Named tuple containing all result file paths
        """
        return ResultPaths(
            functions=self.results_path / "functions.json",
            functions_clean=self.results_path / "functions_clean.json",
            call_graph=self.results_path / "call_graph.json",
            call_graph_clean=self.results_path / "call_graph_clean.json",
            call_graph_tree=self.results_path / "call_graph_tree.txt",
        )

    def _get_known_functions(self, functions_file: Path) -> Set[str]:
        """Get a set of known function names from functions.json.

        This method reads the functions file and extracts valid function names,
        filtering out empty functions, global scopes, and operator functions.

        Args:
            functions_file (Path): Path to the functions.json file

        Returns:
            Set[str]: Set of valid function names
        """
        functions = self.file_handler.read_json(functions_file)
        return {
            func["name"]
            for func in functions
            if func.get("code")
            and func.get("code") not in ["<empty>", "<global>"]
            and not func.get("name", "").startswith("<operator>")
        }

    def _is_system_function(self, name: str) -> bool:
        """Check if a function is a common system function.

        Args:
            name (str): Name of the function to check

        Returns:
            bool: True if the function is a system function, False otherwise
        """
        return name in SYSTEM_FUNCTIONS

    def clean_functions(self, input_file: Path, output_file: Path) -> None:
        """Clean and format the functions data.

        Removes empty functions, global scopes, operator functions, and functions
        with unknown file locations from the input data.

        Args:
            input_file (Path): Path to the input functions file
            output_file (Path): Path where the cleaned functions will be saved
        """
        functions = self.file_handler.read_json(input_file)

        cleaned_functions = [
            func
            for func in functions
            if (
                func.get("code") not in ["<empty>", "<global>"]
                and not func.get("name", "").startswith("<operator>")
                and func.get("code")
                and func.get("file") != "<unknown>"
            )
        ]

        self.file_handler.write_json(cleaned_functions, output_file)

    def clean_call_graph(self, input_file: Path, output_file: Path, functions_file: Path) -> None:
        """Clean and format the call graph data.

        Filters the call graph to only include known functions and system functions,
        removing calls with unknown file locations.

        Args:
            input_file (Path): Path to the input call graph file
            output_file (Path): Path where the cleaned call graph will be saved
            functions_file (Path): Path to the functions file for validation
        """
        known_functions = self._get_known_functions(functions_file)
        calls = self.file_handler.read_json(input_file)

        cleaned_calls = [
            call
            for call in calls
            if (
                (call.get("name") in known_functions or self._is_system_function(call.get("name", "")))
                and call.get("file") != "<unknown>"
            )
        ]

        self.file_handler.write_json(cleaned_calls, output_file)

    def format_call_graph(self, input_file: Path, output_file: Path) -> None:
        """Format the call graph into a tree structure.

        Converts the call graph into a hierarchical tree format, showing the
        relationships between functions and their file locations.

        Args:
            input_file (Path): Path to the input call graph file
            output_file (Path): Path where the formatted tree will be saved
        """
        calls = self.file_handler.read_json(input_file)

        # Create a mapping of function names to their file paths
        function_files = {}
        for call in calls:
            if call["method"] not in function_files and call["method"] != "<global>":
                function_files[call["method"]] = call.get("file", "<unknown>")
            if call["name"] not in function_files and call["name"] != "<global>":
                function_files[call["name"]] = call.get("file", "<unknown>")

        # Group calls by caller
        call_tree = defaultdict(set)
        for call in calls:
            if call["method"] != "<global>" and call["name"] != "<global>":
                call_tree[call["method"]].add(call["name"])

        # Format the output
        output_lines = []
        for caller in sorted(call_tree.keys()):
            caller_file = function_files.get(caller, "<unknown>")
            caller_prefix = (
                "?:" if caller_file == "<unknown>" or self._is_system_function(caller) else f"{caller_file}:"
            )
            output_lines.append(f"{caller_prefix}{caller}")

            for callee in sorted(call_tree[caller]):
                callee_file = function_files.get(callee, "<unknown>")
                callee_prefix = (
                    "?:" if callee_file == "<unknown>" or self._is_system_function(callee) else f"{callee_file}:"
                )
                output_lines.append(f"  {callee_prefix}{callee}")

        self.file_handler.write_text("\n".join(output_lines), output_file)

    def save_raw_results(self, functions_info: List[Dict[str, Any]], call_graph: List[Dict[str, Any]]) -> None:
        """Save raw analysis results to files.

        Saves the raw function information and call graph data to JSON files
        in the results directory.

        Args:
            functions_info (List[Dict[str, Any]]): List of function information dictionaries
            call_graph (List[Dict[str, Any]]): List of call graph entries
        """
        paths = self._get_result_paths()
        self.file_handler.write_json(functions_info, paths.functions)
        self.file_handler.write_json(call_graph, paths.call_graph)

    def _process_results(self) -> None:
        """Process all results by cleaning and formatting them.

        This internal method handles the common processing logic used by both
        get_all_results() and clean_and_format_results().
        """
        paths = self._get_result_paths()

        # Clean functions
        self.clean_functions(paths.functions, paths.functions_clean)

        # Clean call graph
        self.clean_call_graph(paths.call_graph, paths.call_graph_clean, paths.functions_clean)

        # Format call graph tree
        self.format_call_graph(paths.call_graph_clean, paths.call_graph_tree)

    def get_all_results(self, functions_info: List[Dict[str, Any]], call_graph: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get all analysis results in a format suitable for API responses.

        Processes and returns all analysis results in various formats, including
        raw data, cleaned data, and formatted call graph tree.

        Args:
            functions_info (List[Dict[str, Any]]): List of function information dictionaries
            call_graph (List[Dict[str, Any]]): List of call graph entries

        Returns:
            Dict[str, Any]: Dictionary containing all analysis results in different formats:
                - functions: Raw function data
                - call_graph: Raw call graph data
                - cleaned_functions: Cleaned function data
                - cleaned_call_graph: Cleaned call graph data
                - call_graph_tree: Formatted call graph tree as list of strings
        """
        paths = self._get_result_paths()

        # Save raw results
        self.save_raw_results(functions_info, call_graph)

        # Process results
        self._process_results()

        # Read all results
        return {
            "functions": self.file_handler.read_json(paths.functions),
            "call_graph": self.file_handler.read_json(paths.call_graph),
            "cleaned_functions": self.file_handler.read_json(paths.functions_clean),
            "cleaned_call_graph": self.file_handler.read_json(paths.call_graph_clean),
            "call_graph_tree": self.file_handler.read_text(paths.call_graph_tree).split("\n"),
        }

    def clean_and_format_results(self) -> None:
        """Clean and format all analysis results.

        Processes all existing result files in the results directory, cleaning
        and formatting them into various output formats. This method assumes
        that the raw results files already exist in the results directory.
        """
        self._process_results()
        logger.info("Successfully cleaned and formatted all results")

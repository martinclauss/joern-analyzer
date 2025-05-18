# Joern Analyzer

A Python tool for analyzing C/C++ code using Joern, a powerful code analysis platform. This is just a wrapper arround the docker version of joern to generate call graphs and extract function information. It can be used as a standalone tool or via REST API.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/martinclauss/joern-analyzer.git
cd joern_analyzer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure Docker is running and accessible:
```bash
docker --version
```

## Usage

### Command Line Interface

Basic usage:
```bash
./joern_analyzer.py <path-to-code>
```

Example:
```bash
./joern_analyzer.py test_code/simple
```

The tool will:
1. Start a Joern Docker container
2. Import the code into Joern
3. Generate a Code Property Graph (CPG)
4. Analyze the code
5. Generate results in the `results` directory

### REST API

The project includes a REST API (`api.py`) for remote code analysis:

```bash
# Run with default settings (host 127.0.0.1, port 3003, debug mode off)
python api.py

# Run with custom host
python api.py --host 0.0.0.0

# Run with custom port
python api.py --port 8080

# Run with debug mode enabled
python api.py --debug

# Run with custom host, port and debug mode
python api.py --host 0.0.0.0 --port 8080 --debug

# Show available options
python api.py --help
```

The API provides endpoints for:
- `/upload_code` (POST): Upload code for analysis
  - Accepts zip files containing C/C++ source code
  - Returns a unique code_id for the uploaded code
- `/call_graph/<code_id>` (GET): Retrieve analysis results
  - Returns function information and call graph data
  - Includes both raw and cleaned data formats

### API Client

The project includes a REST client (`simple_rest_client.py`) for interacting with the analysis API:

```bash
python simple_rest_client.py
```

The client will:
1. Check if the API is running (default: http://localhost:3003)
2. Create a zip file from the test code
3. Upload the code for analysis
4. Retrieve and display the analysis results

### Test Code

The project includes three example projects in the `test_code/` directory:

1. `test_code/simple/`: A basic project demonstrating function calls and utility operations
   - Simple math operations and utility functions
   - Results in `test_code/simple_results.json`

2. `test_code/complex/`: A more complex project with file I/O and data structures
   - List operations, sorting algorithms, and file handling
   - Results in `test_code/complex_results.json`

3. `test_code/more_complex/`: A sophisticated project with a modular architecture
   - Calculator implementation with core, math, and utility modules
   - Results in `test_code/more_complex_results.json`

Each example project demonstrates different aspects of code analysis and comes with its own results file for reference.

When working with larger code bases it might be necessary to change the `JAVA_OPTS` in `settings.py`, i. e. the maximum heap size (-Xmx8g). The result files get larger as well, e. g. for the `src` directory of https://github.com/vim/vim:

```
$ ls -lah
Permissions Size User Date Modified Name
.rw-r--r--@  62M user   18 May 17:46  call_graph.json
.rw-r--r--@ 6.0M user   18 May 17:46  call_graph_clean.json
.rw-r--r--@ 1.1M user   18 May 17:46  call_graph_tree.txt
.rw-r--r--   25M user   18 May 17:45  cpg.bin
.rw-r--r--@  30M user   18 May 17:46  functions.json
.rw-r--r--@  30M user   18 May 17:46  functions_clean.json
```

And the analysis takes usually longer.

## Output

The analysis results are stored in the `results` directory, with a unique hash-based subdirectory for each analysis run. The following files are generated:

- `functions.json`: Raw function information
  - Contains all functions found in the code
  - Includes function names, locations, and code
- `functions_clean.json`: Cleaned function information
  - Removes empty functions and system functions
  - Filters out global scopes and operator functions
- `call_graph.json`: Raw call graph data
  - Contains all function calls found in the code
  - Includes caller and callee information
- `call_graph_clean.json`: Cleaned call graph data
  - Removes calls to unknown functions
  - Filters out system function calls
- `call_graph_tree.txt`: Formatted call graph in tree structure
  - Hierarchical view of function calls
  - Includes file locations for each function

## Error Messages

Some expected error messages that can be safely ignored:

```
Creating project `cpg.bin` for CPG at `/results/cpg.bin`
Project with name cpg.bin already exists - overwriting
Creating working copy of CPG to be safe
Loading base CPG from: /results/workspace/cpg.bin/cpg.bin.tmp
Adding default overlays to base CPG
The graph has been modified. You may want to use the `save` command to persist changes to disk.  All changes will also be saved collectively on exit
The graph has been modified. You may want to use the `save` command to persist changes to disk.  All changes will also be saved collectively on exit
closing/saving project `cpg.bin`
```

These messages are part of Joern's normal operation and do not impact the analysis results.

## Project Structure

```
joern_analyzer/
├── api.py                        # REST API implementation
├── joern_analyzer.py             # Main analyzer
├── joern_scripts/
│   └── analysis.sc               # Joern analysis scripts
├── README.md                     # This file
├── requirements_dev.txt          # Development dependencies
├── requirements.txt              # Python dependencies
├── results_processor.py          # Results processing and formatting
├── settings.py                   # Configuration settings
├── simple_rest_client.py         # API client
├── test_all_codebases.sh         # Test script for all codebases
├── test_code/                    # Example projects
│   ├── complex/                  # Complex example
│   ├── complex_results.json      # Results for complex example
│   ├── more_complex/             # Advanced example
│   ├── more_complex_results.json # Results for more complex example
│   ├── simple/                   # Basic example
│   └── simple_results.json       # Results for simple example
└── utils/
    ├── docker_manager.py         # Docker container management
    └── file_handler.py           # File operations
```

## Configuration

Configuration settings can be modified in `settings.py`

## License

see [LICENSE](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

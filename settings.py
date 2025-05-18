"""Settings Module

This module contains all configuration settings for the Joern analyzer application.
It defines settings for Docker, analysis parameters, system functions, and file paths.

The module includes:
- Docker configuration for running Joern
- Analysis timeout and output settings
- List of recognized system functions
- File extensions to analyze
- Container and project paths
- Java options for Joern

All settings are typed using TypedDict for better type safety and documentation.
"""

from pathlib import Path
from typing import Set, TypedDict
import shutil


# Docker settings
class JoernSettings(TypedDict):
    """Docker settings specific to Joern container.

    Attributes:
        image: Docker image name and tag
        platform: Target platform for the container
        working_dir: Working directory inside the container
    """

    image: str
    platform: str
    working_dir: str


class DockerSettings(TypedDict):
    """Global Docker configuration settings.

    Attributes:
        joern: Joern-specific Docker settings
        docker_executable: Path to the Docker executable
    """

    joern: JoernSettings
    docker_executable: str


DOCKER_SETTINGS: DockerSettings = {
    "joern": {"image": "ghcr.io/joernio/joern:nightly", "platform": "linux/amd64", "working_dir": "/app"},
    "docker_executable": shutil.which("docker") or "docker",  # Fallback to "docker" if not found
}


# Analysis settings
class TimeoutSettings(TypedDict):
    """Timeout settings for various operations.

    Attributes:
        docker_start: Timeout for Docker container startup (seconds)
        command_execution: Timeout for command execution (seconds)
        server_init: Timeout for server initialization (seconds)
    """

    docker_start: int
    command_execution: int
    server_init: int


class OutputSettings(TypedDict):
    """Output file settings.

    Attributes:
        functions_file: Name of the functions output file
        call_graph_file: Name of the call graph output file
    """

    functions_file: str
    call_graph_file: str


class AnalysisSettings(TypedDict):
    """Analysis configuration settings.

    Attributes:
        timeout: Timeout settings for various operations
        output: Output file settings
    """

    timeout: TimeoutSettings
    output: OutputSettings


ANALYSIS_SETTINGS: AnalysisSettings = {
    "timeout": {"docker_start": 30, "command_execution": 300, "server_init": 5},  # seconds  # seconds  # seconds
    "output": {"functions_file": "functions.json", "call_graph_file": "call_graph.json"},
}

# System functions that should be recognized
SYSTEM_FUNCTIONS: Set[str] = {
    # String manipulation
    "strcpy",
    "strncpy",
    "strcat",
    "strncat",
    "strlen",
    "strcmp",
    "strncmp",
    "strchr",
    "strrchr",
    "strstr",
    "strtok",
    "strtok_r",
    "strspn",
    "strcspn",
    "strpbrk",
    "strcasecmp",
    "strncasecmp",
    "strdup",
    "strndup",
    # Memory operations
    "malloc",
    "calloc",
    "realloc",
    "free",
    "memcpy",
    "memmove",
    "memset",
    "memcmp",
    "memchr",
    "memrchr",
    # File I/O
    "fopen",
    "fclose",
    "fread",
    "fwrite",
    "fprintf",
    "fscanf",
    "fgets",
    "fputs",
    "fseek",
    "ftell",
    "rewind",
    "fflush",
    "feof",
    "ferror",
    "remove",
    "rename",
    "tmpfile",
    "tmpnam",
    # Standard I/O
    "printf",
    "scanf",
    "getchar",
    "putchar",
    "gets",
    "puts",
    "fgetc",
    "fputc",
    "ungetc",
    "perror",
    # Process control
    "exit",
    "abort",
    "atexit",
    "system",
    "getenv",
    "setenv",
    "unsetenv",
    # Error handling
    "assert",
    "errno",
    "strerror",
    # Time functions
    "time",
    "ctime",
    "gmtime",
    "localtime",
    "strftime",
    "mktime",
    # Math functions
    "abs",
    "labs",
    "llabs",
    "div",
    "ldiv",
    "lldiv",
    "rand",
    "srand",
    # Character handling
    "isalpha",
    "isdigit",
    "isalnum",
    "isspace",
    "isupper",
    "islower",
    "toupper",
    "tolower",
    # Signal handling
    "signal",
    "raise",
    "sigaction",
    "sigprocmask",
    # System information
    "getpid",
    "getppid",
    "getuid",
    "getgid",
    "getlogin",
    # Directory operations
    "mkdir",
    "rmdir",
    "chdir",
    "getcwd",
    "opendir",
    "readdir",
    "closedir",
    # Socket operations
    "socket",
    "bind",
    "listen",
    "accept",
    "connect",
    "send",
    "recv",
    "sendto",
    "recvfrom",
    "shutdown",
    "close",
    # Network functions
    "gethostbyname",
    "gethostbyaddr",
    "getaddrinfo",
    "getnameinfo",
    # Thread functions
    "pthread_create",
    "pthread_join",
    "pthread_detach",
    "pthread_exit",
    "pthread_mutex_init",
    "pthread_mutex_lock",
    "pthread_mutex_unlock",
    "pthread_cond_init",
    "pthread_cond_wait",
    "pthread_cond_signal",
}

# File extensions to analyze
C_CPP_EXTENSIONS = {
    # C implementation files
    ".c",
    # C++ implementation files
    ".cpp",
    ".cc",
    ".cxx",
    ".C",
    ".c++",
    ".cp",
    ".CPP",
    # C/C++ header files
    ".h",
    ".hpp",
    ".hh",
    ".hxx",
    ".H",
    ".h++",
}

# Java options for Joern
JAVA_OPTS = ["-Xmx8g", "-Dfile.encoding=UTF-8"]


# Container paths
class ContainerPaths(TypedDict):
    """Container path mappings.

    Attributes:
        app: Path to the application code in container
        results: Path to the results directory in container
        scripts: Path to the analysis scripts in container
    """

    app: str
    results: str
    scripts: str


CONTAINER_PATHS: ContainerPaths = {"app": "/app", "results": "/results", "scripts": "/joern_scripts"}

# Project paths
PATHS = {
    "results_dir": Path(__file__).parent / "results",
    "joern_scripts": Path(__file__).parent / "joern_scripts",
}

# Create required directories
for path in PATHS.values():
    if isinstance(path, Path):
        path.mkdir(parents=True, exist_ok=True)

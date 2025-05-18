import subprocess
from typing import Optional, Tuple, List, Union, Collection, Dict
from pathlib import Path
from os import PathLike

from loguru import logger
from settings import DOCKER_SETTINGS


class DockerManager:
    """Manages Docker container operations."""

    def __init__(self, image: str, platform: str = "linux/amd64"):
        """Initialize the Docker manager.

        Args:
            image: Docker image to use
            platform: Platform to run the container on
        """
        self.image = image
        self.platform = platform
        self.container_id: Optional[str] = None
        self.docker_cmd = DOCKER_SETTINGS["docker_executable"]

    def start_container(
        self,
        image: str,
        command: List[str],
        volumes: Dict[str, Dict[str, str]],
        environment: Dict[str, str],
        working_dir: str = "/app",
    ) -> bool:
        """Start a Docker container with the specified configuration.

        Args:
            image: Docker image to use
            command: Command to run in the container
            volumes: Dictionary mapping host paths to container paths with mode
            environment: Dictionary of environment variables
            working_dir: Working directory inside the container

        Returns:
            bool: True if container started successfully, False otherwise
        """
        try:
            # First check if Docker is running
            try:
                subprocess.run([str(self.docker_cmd), "info"], capture_output=True, check=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"Docker is not running or not accessible: {e.stderr}")
                return False
            except FileNotFoundError:
                logger.error("Docker command not found. Is Docker installed?")
                return False

            # Check if image exists
            try:
                result = subprocess.run(
                    [str(self.docker_cmd), "images", image, "--format", "{{.Repository}}:{{.Tag}}"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                if not result.stdout.strip():
                    logger.error(f"Docker image {image} not found. Pulling...")
                    subprocess.run([str(self.docker_cmd), "pull", image], capture_output=True, check=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to check/pull Docker image: {e.stderr}")
                return False

            # Build the Docker run command
            cmd: List[str] = [str(self.docker_cmd), "run", "--rm", "-d", "--platform", self.platform, "-w", working_dir]

            # Add environment variables
            for key, value in environment.items():
                cmd.extend(["-e", f"{key}={value}"])

            # Add volume mounts
            for host_path, mount_info in volumes.items():
                host_path_str = str(host_path) if isinstance(host_path, (Path, PathLike)) else host_path
                cmd.extend(["-v", f"{host_path_str}:{mount_info['bind']}:{mount_info['mode']}"])

            # Add image and command
            cmd.extend([image] + command)

            logger.debug(f"Executing Docker command: {' '.join(cmd)}")

            # Run the command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Get the container ID
            self.container_id = result.stdout.strip()
            logger.info(f"Container started with ID: {self.container_id}")

            # Verify container is running
            if not self._verify_container_running():
                logger.error("Container failed to start properly")
                return False

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start container. Command: {' '.join(cmd)}\nError: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error starting container: {str(e)}")
            return False

    def stop_container(self) -> bool:
        """Stop the running container.

        Returns:
            bool: True if container stopped successfully, False otherwise
        """
        if not self.container_id:
            logger.warning("No container ID available to stop")
            return False

        logger.info(f"Stopping container {self.container_id}")
        try:
            result = subprocess.run(
                [str(self.docker_cmd), "stop", self.container_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if result.returncode != 0:
                logger.error(f"Error stopping container: {result.stderr}")
                return False

            logger.info("Container stopped successfully")
            self.container_id = None
            return True

        except Exception as e:
            logger.exception(f"Error stopping container: {str(e)}")
            return False

    def execute_command(
        self, command: Union[List[str], Collection[str]], timeout: int = 60, input: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """Execute a command in the running container.

        Args:
            command: List of command arguments to execute
            timeout: Command timeout in seconds
            input: Optional input string to send to the command

        Returns:
            Tuple of (success, stdout, stderr)
        """
        if not self.container_id:
            return False, "", "No container running"

        cmd: List[str] = [str(self.docker_cmd), "exec", self.container_id] + list(command)
        logger.debug(f"Executing command in container: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout, input=input
            )

            if result.stdout:
                logger.debug(f"Command stdout: {result.stdout}")
            if result.stderr:
                logger.error(f"Command stderr: {result.stderr}")

            return result.returncode == 0, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout} seconds")
            return False, "", "Command timed out"
        except Exception as e:
            logger.exception(f"Error executing command: {str(e)}")
            return False, "", str(e)

    def _verify_container_running(self) -> bool:
        """Verify that the container is running.

        Returns:
            bool: True if container is running, False otherwise
        """
        if not self.container_id:
            return False

        cmd: List[str] = [str(self.docker_cmd), "ps", "--filter", f"id={self.container_id}", "--format", "{{.Status}}"]
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                logger.error(f"Error checking container status: {result.stderr}")
                return False

            status = result.stdout.strip()
            logger.debug(f"Container status: {status}")
            return bool(status)

        except Exception as e:
            logger.exception(f"Error verifying container status: {str(e)}")
            return False

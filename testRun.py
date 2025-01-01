import os
import subprocess

# Get the current working directory
current_dir = os.getcwd()

# Docker command to run the KLEE container and execute commands inside it
docker_command = [
    "docker", "run", "--rm", "--platform", "linux/amd64",
    "-v", f"{current_dir}:/home/klee/workspace",  # Mount current directory into the container
    "klee/klee",
    "bash", "-c", "cd workspace/Desktop/klee && python3 testRun.py"
]

# Run the Docker command
try:
    subprocess.run(docker_command, check=True)
    print("Docker command executed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error running Docker command: {e}")

import os
import subprocess

schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "Runs the specified python file, with arguments. Use this when a file is specified",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to run, relative to the working directory (default is the working directory itself)",
                },
                "args": {
                    "type": "array",
                    "description": "An optional list of arguments to use on the specified script",
                },
            },
        },
    },
}

def run_python_file(working_directory: str, file_path: str, args: list[str] | None = None) -> str:
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))
        valid_target_file = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs

        if not valid_target_file:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'

        if not target_file.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", target_file]
        if args != None:
            command.extend(args)

        completed = subprocess.run(command, check=False, timeout=30, text=True, capture_output=True)

        output = ""
        if completed.returncode != 0:
            output += f"Process exited with code {completed.returncode}"

        if (completed.stdout == "" or completed.stdout == None) and (completed.stderr == "" or completed.stderr == None):
            output += "No output produced"

        if completed.stdout != "" or completed.stdout != None:
            output += f"STDOUT: {completed.stdout}"

        if completed.stderr != "" or completed.stderr != None:
            output += f"STDERR: {completed.stderr}"

        return output
    except Exception as e:
        return f"Error: executing Python file: {e}"

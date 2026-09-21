from functools import lru_cache
import shutil
import subprocess
from typing import List, Tuple
from pathlib import Path

from eitherutil import Either, Failure, Success

@lru_cache()
def resolve_exe_path(cmd: str) -> Either[str, Path]:
    """Resolves an executable path for a given command using 'shutil.which'.

    Args:
        command (str): The command to resolve the executable path for. Must be defined in PATH.
    Returns:
        Either[str, Path]: Failure with error message or Success with a Path object to the executable.
    """
    path = shutil.which(cmd)
    if path is None:
        return Failure(f"Executable for command '{cmd}' was not found in PATH.")

    return Success(Path(path))

def run(exe_path: Path, args: List[str], *, capture_output: bool = False, text: bool = True) -> Either[str, Tuple[Path, subprocess.CompletedProcess[str]]]:
    """Runs a given executable with the given arguments using 'subprocess.run'.

    Args:
        exe_path (Path): Path to the executable. For a command use 'resolve_exe_path' first.
        args (List[str]): Trailing arguments after the executable.
        capture_output (bool): Optional flag, when True captures stdout and stdin.
        text (bool): Optional flag, when true enables text mode, which converts bytes to strings.
    Returns:
        Either[str, Tuple[Path, CompletedProcess[str]]]: Failure with error message
            or Success with tuple of executable path and the CompletedProcess result.
    """
    command = f"{exe_path} {" ".join(args)}"
    result = subprocess.run(command, capture_output=capture_output, text=text)
    if result.returncode != 0:
        return Failure(
            f"Execution of {exe_path.name} failed wit code {result.returncode}:\n"
            f" - Executed command: {command}\n"
            f"{f" - Captured stdout: {result.stdout}\n" if result.stdout else ''}"
            f"{f" - Captured stderr: {result.stderr}\n" if result.stderr else ''}"
        )

    return Success((exe_path, result))
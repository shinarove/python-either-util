import shutil
from typing import Iterable, List, Tuple
from pathlib import Path

from eitherutil import Either, Failure, Success

from .validation import validate_path, validate_dir_path

def get_relative_path(inside_path: str | Path, base_path: str | Path) -> Either[str, Path]:
    """Gets the relative path from the inside path to the base path.

    Args:
        inside_path (str | Path): Path inside the base path.
        base_path (str | Path): Base path to a directory which contains the inside path.
    Retruns:
        Either[str, Path]: Left with error message or Right with relative Path from 'base' to 'inside'.
    """
    return (
        validate_path(inside_path)
        .zip(validate_dir_path(base_path))
        .attempt_star(
            lambda inside, base: inside.relative_to(base),
            lambda inside, base, _: f"Could not get relative path. Path '{inside}' is not inside '{base}'."
        )
    )

def glob(dir_path: str | Path, patterns: str | Iterable[str]) -> Either[str, List[Path]]:
    """Wrapper of the 'pathlib.Path.glob' function.
    Supporting multiple patterns and combining them into one result.

    Args:
        dir_path (str | Path): Path to the directory to gather the paths based on the glob patterns.
        patterns (Iterable[str]): Multiple glob patterns to filter paths..
    Returns:
        Either[str, List[Path]]: Failure with error message or Success with list of gathered Path objects.
    """
    def _glob(path: Path) -> List[Path]:
        paths: List[Path] = []
        for pattern in patterns:
            if not pattern:
                continue
            paths.extend(list(path.glob(pattern)))
        return paths

    if isinstance(patterns, str):
        patterns = [patterns]

    return (
        validate_dir_path(dir_path)
        .then(_glob)
    )

def move(src: str | Path, dst: str | Path) -> Either[str, Path]:
    """Wrapper of the 'shutil.move' function.

    Args:
        src (Path): The source path.
        dst (Path): The destination path. Can be a directory.
    Returns:
        Either[str, Path]: Failure with error message or Success with the destination Path object.
    """
    return (
        validate_path(src)
        .attempt(
            lambda path: Path(shutil.move(path, dst)),
            lambda _, exception: str(exception)
        )
    )

def copy2(src: Path, dst: Path) -> Either[str, Path]:
    """Wrapper of the 'shutil.copy2' function.

    Args:
        src (Path): The source path.
        dst (Path): The destination path. Can be a directory.
    Returns:
        Either[str, Path]: Left with error message or Right with the destination path.
    """
    return (
        validate_path(src)
        .attempt(
            lambda path: Path(shutil.copy2(path, dst)),
            lambda _, exception: str(exception)
        )
    )
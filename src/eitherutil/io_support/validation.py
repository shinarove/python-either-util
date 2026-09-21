from typing import Optional, Iterable
from pathlib import Path

from eitherutil import Either, Failure, Success

def validate_path(path: str | Path | Either[str, Path]) -> Either[str, Path]:
    """Validates the path if it exists and returns a Path object on success.

    Args:
        path (str | Path | Either[str, Path]]): The path to be validated.
    Returns:
        Either[str, Path]: Failure with error message or Success with validated Path object.
    """
    if path is None:
        return Failure("Path validation can not be done, giving path is a None value.")

    if isinstance(path, str):
        path = Either.lift(Path(path))
    elif isinstance(path, Path):
        path = Either.lift(path)
    elif isinstance(path, Either):
        if path.is_failure():
            return path
    else:
        raise NotImplementedError

    return path.and_then(
        lambda p:
            Success(p)
            if p.exists() else
            Failure(f"Path does not exist: {p}")
    )

def validate_dir_path(dir_path: str | Path | Either[str, Path]) -> Either[str, Path]:
    """Validates the directory path and returns a Path object on success.
    
    Args:
        dir_path (str | Path | Either[str, Path]): The directory path to be validated.
    Returns:
        Either[str, Path]: Failure with error message or Success with validated Path object.
    """
    return (
        validate_path(dir_path)
        .and_then(
            lambda path: 
                Success(path) 
                if path.is_dir() else 
                Failure(f"Path is not a directory: {path}")
        )
    )

def validate_file_path(file_path: str | Path | Either[str, Path]) -> Either[str, Path]:
    """Validates the file path and returns a Path object on success.
    
    Args:
        file_path (str | Path | Either[str, Path]): The file path to be validated.
    Returns:
        Either[str, Path]: Failure with error message or Succeess with validated Path object.
    """
    return (
        validate_path(file_path)
        .and_then(
            lambda path: 
                Success(path) 
                if path.is_file() else 
                Failure(f"Not a file: {path}")
        )
    )

def validate_parent_path(path: str | Path | Either[str, Path]) -> Either[str, Path]:
    """Validates if the parent of given path exists and is a directory, returns a Path object on success.

    Args:
        file_path (str | Path | Either[str, Path]): The path for which the parent will be validated.
    Returns:
        Either[str, Path]: Failure with error message or Success with validated Path object.
    """
    if path is None:
        return Failure("Path validation can not be done, giving path is a None value.")

    if isinstance(path, str):
        path = Path(path)
    elif isinstance(path, Path):
        pass
    elif isinstance(path, Either):
        if path.is_failure():
            return path
        path = path.unwrap()
    else:
        raise NotImplementedError

    result = validate_dir_path(path.parent)
    if result.is_failure():
        return result
    return Success(path)

def validate_file_extension(file_path: str | Path | Either[str, Path], extensions: Iterable[str]) -> Either[str, Path]:
    """Validates extension on a given file path, returns a Path object on success.
    
    Args:
        file_path (str | Path | Either[str, Path]): The file path where the extension gets validated.
        extensions (Iterable[str]): Valid extensions to check against.
    Returns:
        Either[str, Path]: Failure with error message or Success with validated Path object.
    """
    if file_path is None:
        return Failure("Path validation can not be done, giving path is a None value.")

    if isinstance(file_path, str):
        file_path = Path(file_path)
    elif isinstance(file_path, Path):
        pass
    elif isinstance(file_path, Either):
        if file_path.is_failure():
            return file_path
        file_path = file_path.unwrap()
    else:
        raise NotImplementedError

    if file_path.suffix not in extensions:
        return Failure(
            f"Extension of '{file_path}' does not match list of valid extensions: "
            "[{', '.join(extensions)}]"
        )
    return Success(file_path)

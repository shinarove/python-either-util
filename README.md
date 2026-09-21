Utility library for a Either type implementation.

The `Either` type is defined with either Left as `Failure` value or Right as `Success` value.

Provides support for
* Path validation.
* Filesystem operation (e.g. `move`, `copy2`, `glob`).
* Subprocess handling (e.g. `resolve_exe_path`, `run`).
* Tkinter filedialog abstraction (e.g. `askopenfilename`).

## Installing 

Installing the latest version:

```sh
pip install git+https://github.com/shinarove/python-either-util.git@v0.1.0
```

## Usage

```python
# Example validating file path using the io module:
from eitherutil import io

either_path = io.validate_path("real/path")

if not either_path.is_success():
    error_value = either_path.error()
    # error handling


# Chaining instructions together:
from eitherutil import Either

result = (
    Either.lift(40)
    .then(lambda num: num + 2)
    .and_then(
        lambda num:
        Either.Success(num)
        if num == 42 else
        Either.Failure(f"expected: 42, actual: {num}")
    )
    .then(lambda num: num + 2)
)
```
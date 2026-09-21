import pytest

from eitherutil import Either, Failure, Success

# -------------------
# --- Test is_success()
# -------------------

def test_is_success__on_Success_value__returns_True():
    success = Success(1)
    assert success.is_success()

def test_is_success__on_Failure_value__returns_False():
    failure = Failure(1)
    assert not failure.is_success()

# -------------------
# --- Test is_failure()
# -------------------

def test_is_failure__on_Success_value__returns_False():
    success = Success(1)
    assert not success.is_failure()

def test_is_failure__on_Failure_value__returns_True():
    failure = Failure(1)
    assert failure.is_failure()

# -------------------
# --- Test __bool__()
# -------------------

def test_bool__on_Success_value__returns_True():
    success = Success(1)
    assert success

def test_bool__on_Failure_value__returns_False():
    failure = Failure(1)
    assert not failure

# -------------------
# --- Test unwrap()
# -------------------

def test_unwrap__on_Success_value__returns_value():
    success = Success(1)
    assert success.unwrap() == 1

def test_unwrap__on_Failure_value__raises_ValueError():
    failure = Failure(1)
    with pytest.raises(ValueError):
        failure.unwrap()

# -------------------
# --- Test error()
# -------------------

def test_error__on_Success_value__raises_ValueError():
    success = Success(1)
    with pytest.raises(ValueError):
        success.error()

def test_error__on_Failure_value__returns_value():
    failure = Failure(1)
    assert failure.error() == 1

# -------------------
# --- Test unwrap_or()
# -------------------

def test_unwrap_or__on_Success_value__returns_value():
    success = Success(1)
    assert success.unwrap_or(default=2) == 1

def test_unwrap_or__on_Failure_value__returns_default():
    failure = Failure(1)
    assert failure.unwrap_or(default=2) == 2

# -------------------
# --- Test then()
# -------------------

def test_then__on_Success_value__transforms_Success_value():
    success = Success(1)
    success = success.then(lambda num: num + 1)
    assert success.is_success()
    assert success.unwrap() == 2

def test_then__on_Failure_value__leaves_Failure():
    failure = Failure(1)
    failure = failure.then(lambda num: num + 1)
    assert failure.is_failure()
    assert failure.error() == 1

# -------------------
# --- Test and_then()
# -------------------

def test_and_then__on_Success_value_with_new_Success__returns_new_Success():
    success = Either.lift(1)
    success = success.and_then(lambda num: Success(num + 1))
    assert success.is_success()
    assert success.unwrap() == 2

def test_and_then__on_Success_value_with_new_Failure__returns_new_Failure():
    success = Either.lift(1)
    failure = success.and_then(lambda _: Failure("error"))
    assert failure.is_failure()
    assert failure.error() == "error"

def test_and_then__on_Failure_value_with_new_Success__leaves_Failure():
    failure = Failure("error")
    failure = failure.and_then(lambda _: Success(1))
    assert failure.is_failure()
    assert failure.error() == "error"

def test_and_then__on_Failure_value_with_new_Failure__leaves_Failure():
    failure = Failure("error")
    failure = failure.and_then(lambda _: Failure("new error"))
    assert failure.is_failure()
    assert failure.error() == "error"

# -------------------
# --- Test then_star()
# -------------------

def test_then_start__on_Success_non_Tuple_value__raises_TypeError():
    with pytest.raises(TypeError):
        success = Success(1)
        # Suppress type checker warning for intentional runtime type failure
        success = success.then_star(lambda num1, num2: num1 + num2) # type: ignore

def test_then_star__on_Success_value__transforms_Success_value():
    success = Success((1, 2))
    success = success.then_star(lambda num1, num2: num1 + num2)
    assert success.is_success()
    assert success.unwrap() == 3

def test_then_star__on_Failure_value__leaves_Failure():
    failure = Failure(1)
    failure = failure.then_star(lambda num1, num2: num1 + num2)
    assert failure.is_failure()
    assert failure.error() == 1

# -------------------
# --- Test and_then_star()
# -------------------

def test_and_then_start__on_Success_non_Tuple_value__raises_TypeError():
    with pytest.raises(TypeError):
        success = Success(1)
        # Suppress type checker warning for intentional runtime type failure
        success = success.then_star(lambda num1, num2: Success(num1 + num2)) # type: ignore

def test_and_then_star__on_Success_value_with_new_Success__returns_new_Success():
    success = Either.lift((1, 2))
    success = success.and_then_star(lambda num1, num2: Success(num1 + num2))
    assert success.is_success()
    assert success.unwrap() == 3

def test_and_then_star__on_Success_value_with_new_Failure__returns_new_Failure():
    success = Either.lift((1, 2))
    failure = success.and_then_star(lambda *_: Failure("error"))
    assert failure.is_failure()
    assert failure.error() == "error"

def test_and_then_star__on_Failure_value_with_new_Success__leaves_Failure():
    failure = Failure("error")
    failure = failure.and_then_star(lambda _: Success(1))
    assert failure.is_failure()
    assert failure.error() == "error"

def test_and_then_star__on_Failure_value_with_new_Failure__leaves_Failure():
    failure = Failure("error")
    failure = failure.and_then_star(lambda _: Failure("new error"))
    assert failure.is_failure()
    assert failure.error() == "error"

# -------------------
# --- Test zip()
# -------------------

@pytest.mark.parametrize(
    "value, other, expected",
    [
        (1,                         2,          (1, 2)),
        (1,                         "other",    (1, "other")),
        ((1, 2),                    3,          (1, 2, 3)),
        ((1, ("already", "tuple")), 3,          (1, ("already", "tuple"), 3)),
        ((1, 2),                    (1, 2),     (1, 2, (1, 2))),
    ]
)
def test_zip__on_Success_value_with_Success_value__returns_Tuple_value(value, other, expected):
    success = Either.lift(value)
    success = success.zip(Either.lift(other))
    assert success.is_success()
    assert success.unwrap() == expected

def test_zip__on_Failure_value_with_Success_value__leaves_Failure_value():
    failure = Failure("error")
    failure = failure.zip(Success(1))
    assert failure.is_failure()
    assert failure.error() == "error"

def test_zip__on_Failure_value_with_Failure_value__leaves_Failure_value():
    failure = Failure("error")
    failure = failure.zip(Failure("new error"))
    assert failure.is_failure()
    assert failure.error() == "error"

def test_zip__on_Success_value_with_Failure_value__returns_Failure_value():
    success = Either.lift(1)
    failure = success.zip(Failure("error"))
    assert failure.is_failure()
    assert failure.error() == "error"

# -------------------
# --- Test then_zip()
# -------------------

@pytest.mark.parametrize(
    "value, func, expected",
    [
        (1,                         lambda num: num + 1,            (1, 2)),
        (1,                         lambda _: "other",              (1, "other")),
        ((1, 2),                    lambda args: args[0] + args[1], (1, 2, 3)),
        ((1, ("already", "tuple")), lambda args: args[0] + 2,       (1, ("already", "tuple"), 3)),
        ((1, 2),                    lambda arg: (arg[0], arg[1]),   (1, 2, (1, 2)))
    ]
)
def test_then_zip__on_Success_value__transforms_Success_value(value, func, expected):
    success = Either.lift(value)
    success = success.then_zip(func)
    assert success.is_success()
    assert success.unwrap() == expected

def test_then_zip__on_Failure_value__leaves_Failure_value():
    failure = Failure("error")
    failure = failure.then_zip(lambda num: num + 1)
    assert failure.is_failure()
    assert failure.error() == "error"

# -------------------
# --- Test and_then_zip()
# -------------------

@pytest.mark.parametrize(
    "value, func, expected",
    [
        (1,                         lambda num: Success(num + 1),               (1, 2)),
        (1,                         lambda _: Success("other"),                 (1, "other")),
        ((1, 2),                    lambda args: Success(args[0] + args[1]),    (1, 2, 3)),
        ((1, ("already", "tuple")), lambda args: Success(args[0] + 2),          (1, ("already", "tuple"), 3)),
        ((1, 2),                    lambda arg: Success((arg[0], arg[1])),      (1, 2, (1, 2)))
    ]
)
def test_and_then_zip__on_Success_value_with_new_Success__returns_new_Success(value, func, expected):
    success = Either.lift(value)
    success = success.and_then_zip(func)
    assert success.is_success()
    assert success.unwrap() == expected

def test_and_then_zip__on_Success_value_with_new_Failure__returns_new_Failure():
    success = Either.lift(1)
    failure = success.and_then_zip(lambda _: Failure("error"))
    assert failure.is_failure()
    assert failure.error() == "error"

def test_and_then_zip__on_Failure_value_with_new_Success__leaves_Failure_value():
    failure = Failure("error")
    failure = failure.and_then_zip(lambda num: Success(num + 1))
    assert failure.is_failure()
    assert failure.error() == "error"

def test_and_then_zip__on_Failure_value_with_new_Failure__leaves_Failure_value():
    failure = Failure("error")
    failure = failure.and_then_zip(lambda _: Failure("new error"))
    assert failure.is_failure()
    assert failure.error() == "error"

# -------------------
# --- Test tap_success()
# -------------------

def test_tap_success__on_Success_value__calls_tap_func_and_leaves_Success_value():
    success = Success(1)
    res = 0
    def _add_to_res(num):
        nonlocal res
        res = res + num
    success = success.tap_success(_add_to_res)
    assert success.is_success()
    assert success.unwrap() == 1
    assert res == 1

def test_tap_success__on_Failure_value__calls_not_tap_func_and_leaves_Failure_value():
    failure = Failure("error")
    res = 0
    def _add_to_res(num):
        nonlocal res
        res = res + num
    failure = failure.tap_success(_add_to_res)
    assert failure.is_failure()
    assert failure.error() == "error"
    assert res == 0

# -------------------
# --- Test tap_failure()
# -------------------

def test_tap_failure__on_Success_value__calls_not_tap_func_and_leaves_Success_value():
    success = Success(1)
    error_msg = None
    def _set_error_msg(error):
        nonlocal error_msg
        error_msg = error
    success = success.tap_failure(_set_error_msg)
    assert success.is_success()
    assert success.unwrap() == 1
    assert error_msg is None

def test_tap_failure__on_Failure_value__calls_tap_func_and_leaves_Failure_value():
    failure = Failure("error")
    error_msg = None
    def _set_error_msg(error):
        nonlocal error_msg
        error_msg = error
    failure = failure.tap_failure(_set_error_msg)
    assert failure.is_failure()
    assert failure.error() == "error"
    assert error_msg == "error"

# -------------------
# --- Test tap_both()
# -------------------

def test_tap_both__on_Success_value__calls_on_success_func_and_leaves_Success_value():
    success = Success(1)
    error_msg = None
    res = 0
    def _set_error_msg(error):
        nonlocal error_msg
        error_msg = error
    def _add_to_res(num):
        nonlocal res
        res = res + num
    success = success.tap_both(
        on_failure=_set_error_msg,
        on_success=_add_to_res
    )
    assert success.is_success()
    assert success.unwrap() == 1
    assert error_msg is None
    assert res == 1

def test_tap_both__on_Failure_value__calls_tap_func_and_leaves_Failure_value():
    failure = Failure("error")
    error_msg = None
    res = 0
    def _set_error_msg(error):
        nonlocal error_msg
        error_msg = error
    def _add_to_res(num):
        nonlocal res
        res = res + num
    failure = failure.tap_both(
        on_failure=_set_error_msg,
        on_success=_add_to_res
    )
    assert failure.is_failure()
    assert failure.error() == "error"
    assert error_msg == "error"
    assert res == 0

# -------------------
# --- Test always()
# -------------------

def test_always__on_Success_value__executes_func_with_value_and_leaves_Success_value():
    success = Success(1)
    received = None
    def _fn(val):
        nonlocal received
        received = val
        return "ignored"
    success = success.always(_fn)
    assert success.is_success()
    assert success.unwrap() == 1
    assert received == 1

def test_always__on_Failure_value__executes_func_with_None_and_leaves_Failure_value():
    failure = Failure("error")
    received = "not_called"
    def _fn(val):
        nonlocal received
        received = val
        return "ignored"
    failure = failure.always(_fn)
    assert failure.is_failure()
    assert failure.error() == "error"
    assert received is None

# -------------------
# --- Test and_always()
# -------------------

def test_and_always__on_Success_value_with_new_Success__leaves_Success_value():
    success = Either.lift(1)
    received = None
    def _fn(val):
        nonlocal received
        received = val
        return Success("side-effect")
    success = success.and_always(_fn)
    assert success.is_success()
    assert success.unwrap() == 1
    assert received == 1

def test_and_always__on_Success_value_with_new_Failure__returns_new_Failure():
    success = Either.lift(1)
    received = None
    def _fn(val):
        nonlocal received
        received = val
        return Failure("new error")
    failure = success.and_always(_fn)
    assert failure.is_failure()
    assert failure.error() == "new error"
    assert received == 1

def test_and_always__on_Failure_value_with_new_Success__leaves_Failure_value():
    failure = Failure("error")
    received = "not_called"
    def _fn(val):
        nonlocal received
        received = val
        return Success("side-effect")
    failure = failure.and_always(_fn)
    assert failure.is_failure()
    assert failure.error() == "error"
    assert received is None

def test_and_always__on_Failure_value_with_new_Failure__leaves_Failure_value():
    failure = Failure("error")
    received = "not_called"
    def _fn(val):
        nonlocal received
        received = val
        return Failure("ignored error")
    failure = failure.and_always(_fn)
    assert failure.is_failure()
    assert failure.error() == "error"
    assert received is None

# -------------------
# --- Test attempt()
# -------------------

def test_attempt__on_Success_value_without_exception__returns_new_Success():
    success = Either.lift(10)
    success = success.attempt(
        fn=lambda num: num * 2,
        handle_error=lambda num, exc: f"failed on {num}: {exc}"
    )
    assert success.is_success()
    assert success.unwrap() == 20

def test_attempt__on_Success_value_with_exception__calls_handle_error_and_returns_Failure():
    success = Either.lift(0)
    failure = success.attempt(
        fn=lambda num: 10 / num,
        handle_error=lambda num, exc: f"failed on {num} with {type(exc).__name__}"
    )
    assert failure.is_failure()
    assert failure.error() == "failed on 0 with ZeroDivisionError"

def test_attempt__on_Failure_value__leaves_Failure_and_does_not_call_funcs():
    failure = Failure("initial error")
    fn_called = False
    handler_called = False
    def _fn(_):
        nonlocal fn_called
        fn_called = True
        return 42
    def _handler(*_):
        nonlocal handler_called
        handler_called = True
        return "handled"
    result = failure.attempt(fn=_fn, handle_error=_handler)
    assert result.is_failure()
    assert result.error() == "initial error"
    assert not fn_called
    assert not handler_called

# -------------------
# --- Test attempt_star()
# -------------------

def test_attempt_star__on_Success_non_Tuple_value__raises_TypeError():
    with pytest.raises(TypeError):
        success = Success(1)
        # Suppress type checker warning for intentional runtime type failure
        success = success.attempt_star(  # type: ignore
            fn=lambda num: num * 2,
            handle_error=lambda _, exc: f"failed: {exc}"
        )

def test_attempt_star__on_Success_value_without_exception__returns_new_Success():
    success = Either.lift((10, 2))
    success = success.attempt_star(
        fn=lambda a, b: a // b,
        handle_error=lambda a, b, exc: f"failed on ({a}, {b}): {exc}"
    )
    assert success.is_success()
    assert success.unwrap() == 5

def test_attempt_star__on_Success_value_with_exception__calls_handle_error_and_returns_Failure():
    success = Either.lift((10, 0))
    failure = success.attempt_star(
        fn=lambda a, b: a / b,
        handle_error=lambda a, b, exc: f"failed on ({a}, {b}) with {type(exc).__name__}"
    )
    assert failure.is_failure()
    assert failure.error() == "failed on (10, 0) with ZeroDivisionError"

def test_attempt_star__on_Failure_value__leaves_Failure_and_does_not_call_funcs():
    failure = Failure("initial error")
    fn_called = False
    handler_called = False

    def _fn(*_):
        nonlocal fn_called
        fn_called = True
        return 42

    def _handler(*_):
        nonlocal handler_called
        handler_called = True
        return "handled"

    failure = failure.attempt_star(fn=_fn, handle_error=_handler)
    assert failure.is_failure()
    assert failure.error() == "initial error"
    assert not fn_called
    assert not handler_called

# -------------------
# --- Test fold()
# -------------------

def test_fold__on_Success_value__calls_on_success_and_returns_result():
    success = Success(10)
    failure_called = False

    def _on_failure(err):
        nonlocal failure_called
        failure_called = True
        return f"Error: {err}"

    result = success.fold(
        on_failure=_on_failure,
        on_success=lambda val: f"Success: {val * 2}"
    )
    assert result == "Success: 20"
    assert not failure_called

def test_fold__on_Failure_value__calls_on_failure_and_returns_result():
    failure = Failure("not found")
    success_called = False

    def _on_success(val):
        nonlocal success_called
        success_called = True
        return f"Success: {val * 2}"

    result = failure.fold(
        on_failure=lambda err: f"Error: {err}",
        on_success=_on_success
    )
    assert result == "Error: not found"
    assert not success_called
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, TypeVarTuple, Generic, Never, Union, Callable, Unpack, Optional, Any, Self, Tuple, override, overload

F = TypeVar('F', covariant=True)
S = TypeVar('S', covariant=True)

T = TypeVar('T')
NewS = TypeVar('NewS')
NewF = TypeVar('NewF')
L = TypeVar('L')

Ts = TypeVarTuple('Ts')

T1 = TypeVar('T1')
T2 = TypeVar('T2')
T3 = TypeVar('T3')
T4 = TypeVar('T4')

class Either(Generic[F, S], ABC):

    @classmethod
    def lift(cls, val: L) -> Either[F, L]:
        """Lifts a raw value into an Either context."""
        return Success(val)

    def is_success(self) -> bool:
        return isinstance(self, Success)

    def is_failure(self) -> bool:
        return isinstance(self, Failure)

    def __bool__(self) -> bool:
        return self.is_success()

    @abstractmethod
    def unwrap(self) -> S: ...

    @abstractmethod
    def error(self) -> F: ...

    def unwrap_or(self, default: NewS) -> Union[S, NewS]:
        """Unwraps the Success value, if it is a Failure value returns the given default value."""
        try:
            return self.unwrap()
        except ValueError:
            return default

    @overload
    def then(self: Success[S], fn: Callable[[S], NewS]) -> Success[NewS]: ...
    @overload
    def then(self: Failure[F], fn: Callable[[S], NewS]) -> Failure[F]: ...
    @overload
    def then(self: Either[F, S], fn: Callable[[S], NewS]) -> Either[F, NewS]: ...

    def then(self, fn: Callable[[S], NewS]) -> Either[F, NewS]:
        """Transforms a Success value, leaving Failure unchanged."""
        if isinstance(self, Success):
            return Success(fn(self._value))
        elif isinstance(self, Failure):
            return self
        raise NotImplementedError

    @overload
    def and_then(self: Success[S], fn: Callable[[S], Either[F, NewS]]) -> Either[F, NewS]: ...
    @overload
    def and_then(self: Failure[F], fn: Callable[[S], Either[F, NewS]]) -> Failure[F]: ...
    @overload
    def and_then(self: Either[F, S], fn: Callable[[S], Either[F, NewS]]) -> Either[F, NewS]: ...

    def and_then(self, fn: Callable[[S], Either[F, NewS]]) -> Either[F, NewS]:
        """Chains another Either-returning operation on a Success value, leaving Failure unchanged."""
        if isinstance(self, Success):
            return fn(self._value)
        elif isinstance(self, Failure):
            return self
        raise NotImplementedError

    @overload
    def then_star(self: Success[tuple[Unpack[Ts]]], fn: Callable[[Unpack[Ts]], NewS]) -> Success[NewS]: ...
    @overload
    def then_star(self: Failure[F], fn: Callable[[Unpack[Ts]], NewS]) -> Failure[F]: ...
    @overload
    def then_star(self: Either[F, tuple[Unpack[Ts]]], fn: Callable[[Unpack[Ts]], NewS]) -> Either[F, NewS]: ...

    def then_star(self, fn: Callable[..., NewS]) -> Either[F, NewS]:
        """Unpacks a Success tuple to positional arguments for function fn, leaving Failure unchanged.
        Raises a TypeError when the Success value is not a Tuple.
        """
        if isinstance(self, Success):
            if not isinstance(self._value, tuple):
                raise TypeError(f"Can't unpack non tuple Success value: {type(self._value).__name__}")
            return Success(fn(*self._value))
        elif isinstance(self, Failure):
            return self
        raise NotImplementedError

    @overload
    def and_then_star(self: Success[tuple[Unpack[Ts]]], fn: Callable[[Unpack[Ts]], Either[F, NewS]]) -> Either[F, NewS]: ...
    @overload
    def and_then_star(self: Failure[F], fn: Callable[[Unpack[Ts]], Either[F, NewS]]) -> Failure[F]: ...
    @overload
    def and_then_star(self: Either[F, tuple[Unpack[Ts]]], fn: Callable[[Unpack[Ts]], Either[F, NewS]]) -> Either[F, NewS]: ...

    def and_then_star(self, fn: Callable[..., Either[F, NewS]]) -> Either[F, NewS]:
        """Unpacks a Success tuple to positional arguments for function fn, which itself returns a Either object,
        leaving Failure unchanged.
        """
        if isinstance(self, Success):
            if not isinstance(self._value, tuple):
                raise TypeError(f"Can't unpack non tuple Success value: {type(self._value).__name__}")
            return fn(*self._value)
        elif isinstance(self, Failure):
            return self
        raise NotImplementedError

    @overload
    def zip(self: Either[F, Tuple[Unpack[Ts]]], other: Either[F, NewS]) -> Either[F, Tuple[Unpack[Ts], NewS]]: ...
    @overload
    def zip(self: Either[F, S], other: Either[F, NewS]) -> Either[F, Tuple[S, NewS]]: ...
    
    def zip(self, other: Either[F, NewS]) -> Either[F, Tuple[Any, ...]]:
        """Combines two Either objects into a flat tuple. Nested tuples passed as values remain untouched.
        If Self or Other is Failure returns the Failure value.
        """
        if isinstance(self, Success) and isinstance(other, Success):
            if isinstance(self._value, tuple):
                return Success((*self._value, other._value))
            return Success((self._value, other._value))
        elif isinstance(self, Failure):
            return self
        elif isinstance(other, Failure):
            return other
        raise NotImplementedError

    @overload
    def then_zip(self: Success[Tuple[Unpack[Ts]]], fn: Callable[[Tuple[Unpack[Ts]]], NewS]) -> Success[Tuple[Unpack[Ts], NewS]]: ...
    @overload
    def then_zip(self: Success[S], fn: Callable[[S], NewS]) -> Success[Tuple[S, NewS]]: ...
    @overload
    def then_zip(self: Failure[F], fn: Callable[[Any], NewS]) -> Failure[F]: ...
    @overload
    def then_zip(self: Either[F, Tuple[Unpack[Ts]]], fn: Callable[[Tuple[Unpack[Ts]]], NewS]) -> Either[F, Tuple[Unpack[Ts], NewS]]: ...
    @overload
    def then_zip(self: Either[F, S], fn: Callable[[S], NewS]) -> Either[F, Tuple[S, NewS]]: ...

    def then_zip(self, fn: Callable[[Any], NewS]) -> Either[F, Tuple[Any, ...]]:
        """Transforms a Success value by applying a function and zipping the original value with the result into a flat tuple,
        leaving Failure unchanged.
        """
        if isinstance(self, Success):
            res = fn(self._value)
            if isinstance(self._value, tuple):
                return Success((*self._value, res))
            return Success((self._value, res))
        elif isinstance(self, Failure):
            return self
        raise NotImplementedError

    @overload
    def and_then_zip(self: Success[Tuple[Unpack[Ts]]], fn: Callable[[Tuple[Unpack[Ts]]], Either[F, NewS]]) -> Either[F, Tuple[Unpack[Ts], NewS]]: ...
    @overload
    def and_then_zip(self: Success[S], fn: Callable[[S], Either[F, NewS]]) -> Either[F, Tuple[S, NewS]]: ...
    @overload
    def and_then_zip(self: Failure[F], fn: Callable[[Any], Either[F, NewS]]) -> Failure[F]: ...
    @overload
    def and_then_zip(self: Either[F, Tuple[Unpack[Ts]]], fn: Callable[[Tuple[Unpack[Ts]]], Either[F, NewS]]) -> Either[F, Tuple[Unpack[Ts], NewS]]: ...
    @overload
    def and_then_zip(self: Either[F, S], fn: Callable[[S], Either[F, NewS]]) -> Either[F, Tuple[S, NewS]]: ...

    def and_then_zip(self, fn: Callable[[Any], Either[F, NewS]]) -> Either[F, Tuple[Any, ...]]:
        """Chains another Either-returning operation on a Success value and zips the original value with the new Success result into a flat tuple, 
        leaving Failure unchanged.
        """
        if isinstance(self, Success):
            res = fn(self._value)
            if isinstance(res, Failure):
                return res
            elif isinstance(res, Success):
                if isinstance(self._value, tuple):
                    return Success((*self._value, res._value))
                return Success((self._value, res._value))
        elif isinstance(self, Failure):
            return self
        raise NotImplementedError

    def tap_success(self, fn: Callable[[S], Any]) -> Self:
        """Runs a side-effecting function on a Success value while returning Self unchanged."""
        if isinstance(self, Success):
            _ = fn(self._value)
        return self

    def tap_failure(self, fn: Callable[[F], Any]) -> Self:
        """Runs a side-effecting function on a Failure value while returning Self unchanged."""
        if isinstance(self, Failure):
            _ = fn(self._value)
        return self

    def tap_both(self, on_failure: Callable[[F], Any], on_success: Callable[[S], Any]) -> Self:
        """Runs a side-effecting function on either the Failure or Success value while returning Self unchanged.
        
        Args:
            on_failure ((F) -> None): Side-effecting function to be called on a Failure value. Return value gets ignored.
            on_success ((S) -> None): Side-effecting function to be called on a Success value. Return value gets ignored.
        Returns:
            Self: Unchanged Self.
        """
        if isinstance(self, Failure):
            _ = on_failure(self._value)
            return self
        elif isinstance(self, Success):
            _ = on_success(self._value)
            return self
        raise NotImplementedError

    @overload
    def always(self: Success[S], fn: Callable[[S], Any]) -> Success[S]: ...
    @overload
    def always(self: Failure[F], fn: Callable[[None], Any]) -> Failure[F]: ...
    @overload
    def always(self: Either[F, S], fn: Callable[[Optional[S]], Any]) -> Either[F, S]: ...

    def always(self, fn: Callable[[Any], Any]) -> Either[F, S]:
        """Always executes given function fn. Return value gets always ignored.
        Has similiar effect as tap_both with both functions beeing the same.
        """
        if isinstance(self, Success):
            _ = fn(self._value)
        else:
            _ = fn(None)
        return self

    @overload
    def and_always(self: Success[S], fn: Callable[[S], Either[F, Any]]) -> Either[F, S]: ...
    @overload
    def and_always(self: Failure[F], fn: Callable[[None], Either[F, Any]]) -> Failure[F]: ...
    @overload
    def and_always(self: Either[F, S], fn: Callable[[Optional[S]], Either[F, Any]]) -> Either[F, S]: ...

    def and_always(self, fn: Callable[[Any], Either[F, Any]]) -> Either[F, S]:
        """Always executes given function fn.
        - Returns Self when Self is Success and fn succeeds.
        - Returns Self when Self is Failure.
        - Return fn's Failure when Self is Success and fn fails.

        Args:
            fn ((None) -> Either[F, Any]): Either returning function to be always called.
        Returns:
            Either[F, S]: Failure on Self failure or fn failure or Success on Self success and fn success.
        """
        if isinstance(self, Success):
            res = fn(self._value)
            if isinstance(res, Failure):
                return res
            return self

        _ = fn(None)
        return self

    def attempt(self, fn: Callable[[S], NewS], handle_error: Callable[[S, Exception], F]) -> Either[F, NewS]:
        """Attempts to execute given function fn, when an Exception has been cought
        the given error handling function will run and return it's result as a Failure value.
        """
        if isinstance(self, Success):
            try:
                return Success(fn(self._value))
            except Exception as e:
                return Failure(handle_error(self._value, e))
        elif isinstance(self, Failure):
            return self
        raise NotImplementedError

    @overload
    def attempt_star(self: Success[tuple[Unpack[Ts]]], fn: Callable[[Unpack[Ts]], NewS], handle_error: Callable[[Unpack[Ts], Exception], F]) -> Success[NewS]: ...
    @overload
    def attempt_star(self: Failure[F], fn: Callable[[Unpack[Ts]], NewS], handle_error: Callable[[Unpack[Ts], Exception], F]) -> Failure[F]: ...
    @overload
    def attempt_star(self: Either[F, tuple[Unpack[Ts]]], fn: Callable[[Unpack[Ts]], NewS], handle_error: Callable[[Unpack[Ts], Exception], F]) -> Either[F, NewS]: ...

    def attempt_star(self, fn: Callable[..., NewS], handle_error: Callable[..., F]) -> Either[F, NewS]:
        """Attempts to execute given function fn, while also unpacks the Success tuple to positional arguments.
        When an Exception has been cought the given error handling function will run and return it's result as a Failure value.
        """
        if isinstance(self, Success):
            if not isinstance(self._value, tuple):
                raise TypeError(f"Can't unpack non tuple Success value: {type(self._value).__name__}")
            
            try:
                return Success(fn(*self._value))
            except Exception as e:
                return Failure(handle_error(*self._value, e))
        elif isinstance(self, Failure):
            return self
        raise NotImplementedError

    def fold(self, on_failure: Callable[[F], T], on_success: Callable[[S], T]) -> T:
        """Folds a Either type to a non Either type, by applying one of the corresponding functions."""
        if isinstance(self, Failure):
            return on_failure(self._value)
        elif isinstance(self, Success):
            return on_success(self._value)
        raise NotImplementedError

@dataclass(frozen=True)
class Failure(Either[F, Never]):
    """Represents the failure or exceptional side."""
    _value: F

    @override
    def unwrap(self) -> Never:
        raise ValueError(f"Cannot unwrap a Failure value: {self._value}")

    @override
    def error(self) -> F:
        return self._value


@dataclass(frozen=True)
class Success(Either[Never, S]):
    """Represents the success side."""
    _value: S

    @override
    def unwrap(self) -> S:
        return self._value

    @override
    def error(self) -> Never:
        raise ValueError(f"Cannot get error from a Success value: {self._value}")
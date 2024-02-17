from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import wraps
from typing import Callable

from .exceptions import JsonSerializableValueError


@dataclass
class Validator(ABC):

    _validation_passed: bool = field(repr=False, init=False, default=False)
    _error: JsonSerializableValueError = field(repr=False, init=False)

    @abstractmethod
    def is_valid(self, custom_validators: list[Callable] = []):
        pass

    @property
    def errors(self):
        return self._error.message


def validation_required(func: Callable):

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._validation_passed:
            raise PermissionError(
                f"Cannot call {func.__name__} before calling is_valid()."
            )

        func(self, *args, **kwargs)

    return wrapper

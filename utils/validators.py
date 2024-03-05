from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

from .exceptions import JsonSerializableValueError


@dataclass
class Validator(ABC):
    """
    Abstract class for all validators.

    validators may have custom validators inside them, which then can
    be called via calling super's is_valid and passing those validators.

    Attributes:
        _validation_passed: This attribute must always checked before calling
            core/state changing methods, you can use 'validation_required'
            decorator for this.
        _error: a ValueError which can be converted to json easialy,
        DON'T read error messages from this, use 'errors' property/
    """

    _validation_passed: bool = field(repr=False, init=False, default=False)
    _error: JsonSerializableValueError = field(repr=False, init=False)

    @abstractmethod
    def is_valid(self, custom_validators: list[Callable] = []):
        """
        You must call the abstract validators from here, then
        call each custom validator from children in 'custom_validators'.

        All validators must raise 'JsonSerializableValueError' if the provided
        data is not valid, so here you can catch them and inform users with
        human friendly error messages.
        """
        pass

    @property
    def errors(self):
        """Human friendly error messages"""
        return self._error.message

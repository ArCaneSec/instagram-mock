from functools import wraps
from typing import Callable


def validation_required(func: Callable):

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._validation_passed:
            raise PermissionError(
                f"Cannot call {func.__name__} before calling is_valid()."
            )

        func(self, *args, **kwargs)

    return wrapper

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

from rest_framework.exceptions import ValidationError

from .exceptions import JsonSerializableValueError

NAME_EXT_PATTERN = r"^[^\\/<>%#{}]{1,50}\.(?<=\.)(\w{3,4}$)"


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


def validate_content(content):
    """
    Validating extension and content size.

    If content type is not valid, or content type does not match
    with the extension in file name, validation will not pass.
    """

    extension = re.match(NAME_EXT_PATTERN, content.name).group(1)
    if extension is None:
        raise ValidationError(
            {
                "error": "Invalid file name",
                "code": "invalidName",
            }
        )

    valid_extensions = {}
    valid_extensions["video/mp4"] = "mp4"
    valid_extensions["image/gif"] = "gif"
    valid_extensions["image/jpeg"] = "jpeg"
    valid_extensions["image/jpg"] = "jpg"
    valid_extensions["image/png"] = "png"
    # pattern = r"^.[^.\\/<>%#(){}]{1,20}\.(png|jpeg|gif|png|mp4)?$"
    if not (ct_type := valid_extensions.get(content.content_type)):
        raise ValidationError(
            {
                "error": "Invalid file type, supported types are:"
                " mp4, gif, jpeg, jpg png.",
                "code": "invalidExtension",
            }
        )
    if extension != ct_type:
        raise ValidationError(
            {
                "error": "Name extension and content-type are not consistent.",
                "code": "inconsistentExtension",
            }
        )
    if not 1 < content.size / 1024 < 20000:
        raise ValidationError(
            {"error": "invalid file size.", "code": "invalidSize"}
        )
    content.extension = extension.lower()
    return content

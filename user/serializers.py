import re

from rest_framework import serializers

from . import models as m
from . import validators as v


class SignUpRequest(serializers.Serializer):
    username = serializers.CharField(
        max_length=250,
    )
    firstName = serializers.CharField(max_length=250, source="first_name")
    lastName = serializers.CharField(max_length=250, source="last_name")
    profile = serializers.ImageField(required=False)
    phoneNumber = serializers.CharField(
        max_length=11, required=False, source="phone_number"
    )
    email = serializers.EmailField(required=False)
    password = serializers.CharField(max_length=250)

    def validate_password(self, password: str) -> bool:
        pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z\d]{8,}$"
        if not re.match(pattern, password):
            raise serializers.ValidationError("Password is weak.")

    def validate(self, data: dict):
        email = data.get("email")
        username = data.get("username")
        phone = data.get("phone_number")

        if not (email or phone):
            raise serializers.ValidationError(
                "'email' or 'phoneNumber' must be provided.", "non_unique"
            )

        if not v.validate_uniqueness(username, email, phone):
            raise serializers.ValidationError(
                "'username', 'email' and 'phoneNumber' must be unique",
                "non_unique",
            )

        return data

    def create(self, validated_data):
        return m.User.objects.create(**validated_data)

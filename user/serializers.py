from rest_framework import serializers

from . import models as m
from . import validators as v


class SignUpRequest(serializers.Serializer):
    username = serializers.CharField(
        max_lenght=250,
    )
    first_name = serializers.CharField(max_lenght=250, source="firstName")
    last_name = serializers.CharField(max_lenght=250, source="lastName")
    profile = serializers.ImageField(required=False)
    phone_number = serializers.CharField(
        max_length=11, required=False, source="phoneNumber"
    )
    email = serializers.EmailField(required=False)
    password = serializers.CharField(
        max_length=250, validators=[v.validate_password]
    )

    def validate(self, data: dict):
        email = data.get("email")
        username = data.get("username")
        phone = data.get("phoneNumber")

        if not (email and phone):
            raise serializers.ValidationError(
                "'email' or 'phoneNumber' must be provided."
            )

        if not v.validate_uniqueness(username, email, phone):
            raise serializers.ValidationError(
                "'username', 'email' and 'phoneNumber' must be unique"
            )

        return data

    def create(self, validated_data):
        return m.User(**validated_data)

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
    nickName = serializers.CharField(
        max_length=250, source="nickname", required=False
    )
    profile = serializers.ImageField(required=False)
    phoneNumber = serializers.CharField(
        max_length=11, required=False, source="phone_number"
    )
    email = serializers.EmailField(required=False)
    password = serializers.CharField(max_length=250)

    def validate_username(self, username):
        if not v.validate_username(username):
            raise serializers.ValidationError({
                "error": "username is not unique.",
                "code": "nonUniqueUserName",
            })
        return username

    def validate_password(self, password: str) -> bool:
        pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$"
        if not re.match(pattern, password):
            raise serializers.ValidationError({
                "error": "Password must contain atleast 8 characters,"
                " 1 one lowercase and 1 uppercase letter and 1 digit.",
                "code": "weakPassword",
            })
        return password

    def validate_phoneNumber(self, phoneNumber: str):
        if not phoneNumber.isdigit():
            raise serializers.ValidationError({
                "error": "phoneNumber must be digit only.",
                "code": "nonDigitNumber",
            })
        if not v.validate_phone(phoneNumber):
            raise serializers.ValidationError({
                "error": "phoneNumber is not unique",
                "code": "nonUniquePhoneNumber",
            })
        return phoneNumber

    def validate_email(self, email):
        if not v.validate_email(email):
            raise serializers.ValidationError(
                {"error": "email is not unique.", "code": "nonUniqueEmail"}
            )
        return email

    def validate(self, data: dict):
        return data

    def create(self, validated_data):
        return m.User.objects.create(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=250)
    password = serializers.CharField(max_length=250)


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.User
        fields = [
            "username",
            "nickname",
            "first_name",
            "last_name",
            "profile",
            "biography",
            "email",
            "phone_number",
            "total_followers",
            "total_followings",
        ]

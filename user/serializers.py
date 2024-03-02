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
            raise serializers.ValidationError(
                {
                    "error": "username is not unique.",
                    "code": "nonUniqueUserName",
                }
            )
        return username

    def validate_password(self, password: str) -> bool:
        pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$"
        if not re.match(pattern, password):
            raise serializers.ValidationError(
                {
                    "error": "Password must contain atleast 8 characters,"
                    " 1 one lowercase and 1 uppercase letter and 1 digit.",
                    "code": "weakPassword",
                }
            )
        return password

    def validate_phoneNumber(self, phoneNumber: str):
        if not phoneNumber.isdigit():
            raise serializers.ValidationError(
                {
                    "error": "phoneNumber must be digit only.",
                    "code": "nonDigitNumber",
                }
            )
        if not v.validate_phone(phoneNumber):
            raise serializers.ValidationError(
                {
                    "error": "phoneNumber is not unique",
                    "code": "nonUniquePhoneNumber",
                }
            )
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


class UserContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.User
        fields = [
            "username",
            "nickname",
        ]


class UserDataSerializer(serializers.ModelSerializer):
    userName = serializers.CharField(source="username")
    nickName = serializers.CharField(source="nickname")
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")
    phoneNumber = serializers.CharField(source="phone_number")
    totalFollowers = serializers.IntegerField(source="total_followers")
    totalFollowings = serializers.IntegerField(source="total_followings")
    totalFollowRequests = serializers.IntegerField(
        source="total_follow_requests"
    )

    class Meta:
        model = m.User
        fields = [
            "userName",
            "nickName",
            "firstName",
            "lastName",
            "profile",
            "biography",
            "email",
            "phoneNumber",
            "totalFollowers",
            "totalFollowings",
            "totalFollowRequests",
        ]
        read_only_fields = [
            "totalFollowers",
            "totalFollowings",
            "totalFollowRequests",
        ]
        write_only_fields = ["password"]

    def validate(self, attrs):
        pass

    def create(self, validated_data):
        pass
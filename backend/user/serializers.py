from rest_framework import serializers

from . import models as m
from . import validators as v


class LowerCharField(serializers.CharField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        return data.lower()


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
    password = serializers.CharField(
        max_length=250, validators=[m.User.validate_password]
    )

    def validate_username(self, username):
        if not v.validate_username(username):
            raise serializers.ValidationError(
                {
                    "error": "username is not unique.",
                    "code": "nonUniqueUserName",
                }
            )
        return username

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
        email = data.get("email")
        phone_number = data.get("phone_numer")
        if not (email or phone_number):
            raise serializers.ValidationError(
                {
                    "error": "You have to provide an email address "
                    "or phone number "
                    "in order to sign up.",
                    "code": "invalidData",
                }
            )
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
    userName = LowerCharField(source="username", read_only=True)
    nickName = serializers.CharField(source="nickname", required=False)
    firstName = serializers.CharField(source="first_name", required=False)
    lastName = serializers.CharField(source="last_name", required=False)
    profile = serializers.ImageField(required=False)
    biography = serializers.CharField(max_length=1000, required=False)
    email = serializers.EmailField(required=False)
    phoneNumber = serializers.CharField(source="phone_number", required=False)
    totalFollowers = serializers.IntegerField(
        source="total_followers", read_only=True
    )
    totalFollowings = serializers.IntegerField(
        source="total_followings", read_only=True
    )
    totalFollowRequests = serializers.IntegerField(
        source="total_follow_requests", read_only=True
    )
    totalPosts = serializers.IntegerField(
        source="total_posts", read_only=True
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
            "totalPosts",
        ]

    def validate_email(self, email):
        m.User.validate_email(email)
        return email

    def validate_phoneNumber(self, phone_number):
        m.User.validate_phone_number(phone_number)
        return phone_number

    def validate(self, attrs: dict):
        if not attrs:
            raise serializers.ValidationError(
                {"error": "invalid data", "code": "invalidData"}
            )
        user = self.context["request"].user
        for key, value in attrs.items():
            if getattr(user, key) == value:
                attrs.pop(key)

        return super().validate(attrs)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class UserSettingsSerializer(serializers.Serializer):
    userName = LowerCharField(source="username", required=False)
    password = serializers.CharField(required=False)
    newPassword = serializers.CharField(
        required=False,
        validators=[m.User.validate_password],
        source="new_password",
    )
    isPrivate = serializers.BooleanField(source="is_private", required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError(
                {"error": "invalid data.", "code": "invalidData"}
            )
        if (
            attrs.get("username") or attrs.get("new_password")
        ) and not attrs.get("password"):
            raise serializers.ValidationError(
                {
                    "error": "you cannot change these fields"
                    " without entering your password.",
                    "code": "passwordRequired",
                }
            )

        return super().validate(attrs)


class OtherUserSerializer(UserDataSerializer):
    class Meta:
        model = m.User
        fields = [
            "userName",
            "nickName",
            "firstName",
            "lastName",
            "profile",
            "biography",
            "totalFollowers",
            "totalFollowings",
            "totalPosts",
        ]
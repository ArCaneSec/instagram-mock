import re

from rest_framework import serializers

from . import models as m

NAME_EXT_PATTERN = r"^[^.\\/<>%#(){}]{1,50}\.(?<=\.)(\w{3,4}$)"


class CreatePostSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    content = serializers.FileField(max_length=54)
    caption = serializers.CharField(max_length=1000, required=False)
    content_type = serializers.CharField()

    def validate_content(self, content):
        valid_extensions = {}
        valid_extensions["audio/mp4"] = "mp4"
        valid_extensions["image/gif"] = "gif"
        valid_extensions["image/jpeg"] = "jpeg"
        valid_extensions["image/jpg"] = "jpg"
        valid_extensions["image/png"] = "png"
        # pattern = r"^.[^.\\/<>%#(){}]{1,20}\.(png|jpeg|gif|png|mp4)?$"
        if not (ct_type := valid_extensions.get(content.content_type)):
            raise serializers.ValidationError({
                "error": "Invalid file type, supported types are:"
                " mp4, gif, jpeg, jpg png.",
                "code": "invalidExtension",
            })
        if self.initial_data["extension"] != ct_type:
            raise serializers.ValidationError({
                "error": "Name extension and content-type are not consistent.",
                "code": "inconsistentExtension",
            })
        if not 1 < content.size / 1024 < 20000:
            raise serializers.ValidationError(
                {"error": "invalid file size.", "code": "invalidSize"}
            )
        return content

    def to_internal_value(self, data):
        try:
            content_name = data.get("content").name
        except AttributeError:
            return super().to_internal_value(data)

        try:
            data["extension"] = re.match(NAME_EXT_PATTERN, content_name)[
                1
            ]  # matching the second group
        except TypeError:
            raise serializers.ValidationError(
                {"error": "invalid file name.", "code": "invalidName"}
            )
        data["content_type"] = data["extension"]
        return super().to_internal_value(data)

    def create(self, validated_data):
        return m.Post.objects.create(**validated_data)

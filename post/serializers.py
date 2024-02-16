import re

from django.db.models import QuerySet
from rest_framework import serializers

from user.models import User

from . import models as m

# Pattern for extracting extension from file names.
NAME_EXT_PATTERN = r"^[^.\\/<>%#(){}]{1,50}\.(?<=\.)(\w{3,4}$)"


class UploadPostFileSerializer(serializers.Serializer):
    content = serializers.FileField(max_length=54)
    content_type = serializers.CharField()

    def to_internal_value(self, data):
        """
        Extracting extention from file name and putting it
        into 'data' dict.
        """

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

    def validate_content(self, content):
        """
        Validating extension and content size.

        If content type is not valid, or content type does not match
        with the extension in file name, validation will not pass.
        """

        valid_extensions = {}
        valid_extensions["video/mp4"] = "mp4"
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


class CreatePostSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    caption = serializers.CharField(max_length=1000, required=False)
    tags = serializers.ListField(required=False, max_length=10)
    files = serializers.ListField(max_length=10)

    def validate_tags(self, tags):
        """
        Validating users that are being tagged in the post.

        If any user within tag is not valid (invalid, inactive, deleted),
        whole data will be marked as invalid.
        """

        tags = set(tags)
        users = User.objects.filter(
            is_active=True, username__in=tags
        ).distinct()
        usernames = users.values_list("username", flat=True)
        if tags.difference(usernames):
            raise serializers.ValidationError(
                {"error": "user not found", "code": "userNotFound"}
            )

        tags = users
        return tags

    def validate_files(self, files):
        """
        Validating files ids within the post.

        If any file is invalid, whole data will be marked as invalid.
        """

        files = set(files)
        try:
            pf = m.PostFile.objects.filter(
                pk__in=files,
                user=self.context["request"].user,
                post__isnull=True,
            ).distinct()
        except ValueError:
            raise serializers.ValidationError(
                {"error": "invalid file value.", "code": "invalidFile"}
            )

        pf_id_list = pf.values_list("id", flat=True)
        if files.difference(pf_id_list):
            raise serializers.ValidationError(
                {"error": "file not found.", "code": "fileNotFound"}
            )

        return pf

    def create(self, validated_data: dict):
        post_files: QuerySet[m.PostFile] = validated_data.pop("files")

        # Post can have 0 tags, thats why we are passing.
        try:
            tags = validated_data.pop("tags")
        except ValueError:
            pass

        post = m.Post.objects.create(**validated_data)

        # Updating junction table if tags exists.
        if tags:
            post.tags.set([user.pk for user in tags])

        # Changing PostFile's post values from null to 'post' id.
        post_files.update(post=post)
        return post

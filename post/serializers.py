import re

from django.db.models import QuerySet
from rest_framework import serializers

from comment.models import Comment
from user.models import User
from utils.validators import validate_content

from . import models as m

# Pattern for extracting extension from file names.
NAME_EXT_PATTERN = r"^[^.\\/<>%#{}]{1,50}\.(?<=\.)(\w{3,4}$)"


class UploadPostFileSerializer(serializers.Serializer):
    content = serializers.FileField(max_length=54)
    content_type = serializers.CharField()

    # def to_internal_value(self, data):
    #     """
    #     Extracting extention from file name and putting it
    #     into 'data' dict.
    #     """

    #     try:
    #         content_name = data.get("content").name
    #     except AttributeError:
    #         return super().to_internal_value(data)

    #     try:
    #         data["extension"] = re.match(NAME_EXT_PATTERN, content_name)[
    #             1
    #         ]  # matching the second group
    #     except TypeError:
    #         raise serializers.ValidationError(
    #             {"error": "invalid file name.", "code": "invalidName"}
    #         )
    #     data["content_type"] = data["extension"]
    #     return super().to_internal_value(data)

    def validate_content(self, content):
        """
        Validating extension and content size.

        If content type is not valid, or content type does not match
        with the extension in file name, validation will not pass.
        """
        # if not content:
        #     raise serializers.ValidationError(
        #         {"error": "content field is required.", "code": "invalidData"}
        #     )

        valid_extensions = {}
        valid_extensions["video/mp4"] = "mp4"
        valid_extensions["image/gif"] = "gif"
        valid_extensions["image/jpeg"] = "jpeg"
        valid_extensions["image/jpg"] = "jpg"
        valid_extensions["image/png"] = "png"
        # pattern = r"^.[^.\\/<>%#(){}]{1,20}\.(png|jpeg|gif|png|mp4)?$"
        if not (ct_type := valid_extensions.get(content.content_type)):
            raise serializers.ValidationError(
                {
                    "error": "Invalid file type, supported types are:"
                    " mp4, gif, jpeg, jpg png.",
                    "code": "invalidExtension",
                }
            )
        if self.initial_data["extension"] != ct_type:
            raise serializers.ValidationError(
                {
                    "error": "Name extension and content-type are not consistent.",
                    "code": "inconsistentExtension",
                }
            )
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
    hashtags = serializers.ListField()

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

    def to_internal_value(self, data):
        caption = data.get("caption")
        hashtags_pattern = r"(?:\r|^| )(?:\#)([a-z0-9]{1,250})\b"
        data["hashtags"] = set(re.findall(hashtags_pattern, caption))
        return super().to_internal_value(data)

    def validate_hashtags(self, hashtags):
        hashtags = set(hashtags)
        db_hashtags_obj = m.Hashtag.objects.filter(title__in=hashtags)
        db_hashtags = db_hashtags_obj.values_list("title", flat=True)
        diffs = hashtags.difference(db_hashtags)
        if not diffs:
            return db_hashtags_obj.values_list("id", flat=True)

        m.Hashtag.objects.bulk_create(
            [m.Hashtag(title=title) for title in diffs]
        )

        # Here the hashtags are updated with the newly created ones
        # since querysets are  lazy.
        return db_hashtags_obj.values_list("id", flat=True)

    def create(self, validated_data: dict):
        post_files: QuerySet[m.PostFile] = validated_data.pop("files")

        tags = validated_data.pop("tags", None)
        hashtags = validated_data.pop("hashtags", None)
        post = m.Post.objects.create(**validated_data)

        # Updating junction table if tags exists.
        if tags:
            post.tags.set(tags)

        if hashtags:
            post.hashtags.set(hashtags)

        # Changing PostFile's post values from null to 'post' id.
        post_files.update(post=post)
        return post


class PostFileSerializer(serializers.ModelSerializer):
    contentType = serializers.CharField(source="content_type")

    class Meta:
        model = m.PostFile
        fields = ["contentType", "content"]


class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "profile"]


class CommentSerializer(serializers.Serializer):
    user = UserMinimalSerializer()
    content = serializers.CharField(max_length=1000)
    createdAt = serializers.DateTimeField(source="created_at")
    likes = serializers.IntegerField(source="total_likes")


class PostSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer()
    tags = UserMinimalSerializer(many=True)
    comments = CommentSerializer(many=True)
    likes = serializers.IntegerField(source="total_likes")
    files = PostFileSerializer(many=True, source="postfile_set")

    class Meta:
        model = m.Post
        fields = [
            "id",
            "user",
            "caption",
            "tags",
            "comments",
            "likes",
            "files",
        ]


class PostCommentSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=1000)


class DeletePostCommentSerializer(serializers.Serializer):
    comment_id = serializers.IntegerField()

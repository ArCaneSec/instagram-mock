import re

from rest_framework import serializers

from post.serializers import UserMinimalSerializer
from user.models import User
from utils.validators import validate_content

from . import models as m


class UploadStorySerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    caption = serializers.CharField(max_length=1000)
    content = serializers.FileField(
        max_length=54, validators=[validate_content]
    )
    privacy = serializers.CharField(source="privacy_type")
    tags = serializers.ListField(read_only=True)

    def _extract_tags(self):
        caption = self.data["caption"]
        pattern = r"(?:@)([a-z][a-z\d._]{2,250})(?:$| |\n)"
        extracted_tags = re.findall(pattern, caption)
        tags = User.objects.filter(username__in=extracted_tags, is_active=True)
        return tags

    def create(self, validated_data):
        tags = self._extract_tags()
        validated_data["content_type"] = validated_data["content"].extension
        story = m.Story.objects.create(**validated_data)
        story.tags.set(tags)
        return story


class StorySerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer()
    tags = UserMinimalSerializer(many=True)

    class Meta:
        model = m.Story
        fields = ["user", "content_type", "content", "caption", "tags"]


class FullStorySerializer(StorySerializer):
    views = UserMinimalSerializer(many=True)
    likes = UserMinimalSerializer(many=True)

    class Meta(StorySerializer.Meta):
        fields = StorySerializer.Meta.fields + ["views", "likes"]

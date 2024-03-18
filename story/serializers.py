import re

from rest_framework import serializers

from user.models import User

from . import models as m


class UploadStorySerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    caption = serializers.CharField(max_length=1000)
    content = serializers.FileField()
    privacy = serializers.CharField(source="privacy_type")
    tags = serializers.ListField(read_only=True)

    def _extract_tags(self):
        caption = self.data["caption"]
        pattern = r"(?:@)([a-z][a-z\d._]{2,250})(?:$| |\n)"
        extracted_tags = re.findall(pattern, caption)
        tags = User.objects.filter(username__in=extracted_tags, is_active=True)
        return tags

    def validate(self, data):
        super().validate()
        data["tags"] = self._extract_tags()
        return data
    
    def create(self, validated_data):
        story = m.Story.objects.create(**validated_data)
        story.tags.set(validated_data["tags"])
        return story

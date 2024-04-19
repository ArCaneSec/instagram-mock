import datetime

from utils.model_utils import generate_path
from django.db import models as m
from user import models as u

# Create your models here.


def _get_story_lifetime():
    return datetime.datetime.now() + datetime.timedelta(days=1)


class StoryViews(m.Model):
    story = m.ForeignKey("Story", on_delete=m.CASCADE)
    user = m.ForeignKey(u.User, on_delete=m.CASCADE)


class Story(m.Model):

    class ContentType(m.TextChoices):
        IMAGE = "IMG", "IMAGE"
        VIDEO = "VID", "VIDEO"

    class PrivacyType(m.TextChoices):
        NORMAL = "NRL", "NORMAL"
        CLOSE_FRIEND = "CLS", "CLOSE_FRIEND"

    user = m.ForeignKey(u.User, on_delete=m.CASCADE)
    content_type = m.CharField(choices=ContentType.choices, max_length=3)
    content = m.FileField(
        upload_to=generate_path
    )
    caption = m.TextField(null=True, blank=True)
    privacy_type = m.CharField(choices=PrivacyType.choices, max_length=3)
    active_until = m.DateTimeField(default=_get_story_lifetime)
    views = m.ManyToManyField(
        u.User, through=StoryViews, related_name="user_story_views", blank=True
    )
    tags = m.ManyToManyField(
        u.User, related_name="user_story_tags", blank=True
    )
    likes = m.ManyToManyField(
        u.User, related_name="user_story_likes", blank=True
    )

    def save(self, *args, **kwargs):
        if self.privacy_type.lower() == "closefriend":
            self.privacy_type = Story.PrivacyType.CLOSE_FRIEND
        else:
            self.privacy_type = Story.PrivacyType.NORMAL

        match self.content_type:
            case "png" | "jpeg" | "jpg" | "gif":
                self.content_type = self.ContentType.IMAGE
            case "mp4":
                self.content_type = self.ContentType.VIDEO
            case _:
                raise ValueError("invalid extension type.")

        super().save(*args, **kwargs)

import datetime

from django.db import models as m

from user import models as u

# Create your models here.


def _get_story_lifetime():
    return datetime.datetime.now() + datetime.timedelta(days=1)


class StoryViews(m.Model):
    story = m.ForeignKey("Story", on_delete=m.CASCADE)
    user = m.ForeignKey(u.User, on_delete=m.SET_NULL)


class Story(m.Model):

    class ContentType(m.TextChoices):
        IMAGE = "IMG", "IMAGE"
        VIDEO = "VID", "VIDEO"

    class PrivacyType(m.TextChoices):
        NORMAL = "NRL", "NORMAL"
        CLOSE_FRIEND = "CLS", "CLOSE_FRIEND"

    user = m.ForeignKey(u.User, on_delete=m.SET_NULL)
    content_type = m.CharField(choices=ContentType.choices)
    content = m.TextField()
    privacy_type = m.CharField(choices=PrivacyType.choices)
    active_until = m.DateTimeField(default=_get_story_lifetime)
    views = m.ManyToManyField(u.User, through=StoryViews)
    tags = m.ManyToManyField(u.User)
    likes = m.ManyToManyField(u.User)

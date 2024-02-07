from django.db import models as m

from user import models as u

# Create your models here.


class PostLikes(m.Model):
    user = m.ForeignKey(u.User, on_delete=m.CASCADE)
    post = m.ForeignKey("Post", on_delete=m.CASCADE)
    date = m.DateTimeField(auto_now_add=True)


class Post(m.Model):
    class ContentType(m.TextChoices):
        IMAGE = "IMG", "IMAGE"
        VIDEO = "VID", "VIDEO"
        REEL = "REL", "REEL"

    user = m.ForeignKey(u.User, on_delete=m.CASCADE)
    content_type = m.CharField(choices=ContentType.choices, max_length=3)
    content = m.TextField()
    caption = m.TextField(null=True, blank=True)
    is_active = m.BooleanField(default=True)
    is_deleted = m.BooleanField(default=False)
    tags = m.ManyToManyField(u.User, related_name="user_tags")
    likes = m.ManyToManyField(
        u.User, through=PostLikes, related_name="user_likes"
    )
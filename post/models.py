from datetime import date

from django.db import models as m

from user import models as u

# Create your models here.


class PostLikes(m.Model):
    user = m.ForeignKey(u.User, on_delete=m.CASCADE)
    post = m.ForeignKey("Post", on_delete=m.CASCADE)
    date = m.DateTimeField(auto_now_add=True)


class PostFile(m.Model):
    class ContentType(m.TextChoices):
        IMAGE = "IMG", "IMAGE"
        VIDEO = "VID", "VIDEO"
        REEL = "REL", "REEL"

    user = m.ForeignKey(u.User, on_delete=m.CASCADE)
    post = m.ForeignKey("Post", on_delete=m.CASCADE, null=True)
    content_type = m.CharField(choices=ContentType.choices, max_length=3)
    content = m.FileField(upload_to="static/users/posts/")
    created_at = m.DateField(auto_now_add=True)

    @staticmethod
    def specific_date_uploads(user: u.User, specific_date: date) -> int:
        return PostFile.objects.filter(
            user=user,
            created_at=specific_date,
            post__isnull=True,
        ).count()

    def save(self, *args, **kwargs):
        match self.content_type:
            case "gif" | "jpeg" | "jpg" | "png":
                self.content_type = self.ContentType.IMAGE
            case "mp4":
                self.content_type = self.ContentType.VIDEO
            case "mkv":
                self.content_type = self.ContentType.REEL
            case _:
                raise ValueError("Invalid file extension.")

        super().save(*args, **kwargs)


class Post(m.Model):
    user = m.ForeignKey(u.User, on_delete=m.CASCADE)
    caption = m.TextField(null=True, blank=True)
    is_active = m.BooleanField(default=True)
    is_deleted = m.BooleanField(default=False)
    tags = m.ManyToManyField(u.User, related_name="user_tags", blank=True)
    likes = m.ManyToManyField(
        u.User,
        through=PostLikes,
        related_name="user_likes",
        blank=True,
    )
    created_at = m.DateTimeField(auto_now_add=True)
    updated_at = m.DateTimeField(auto_now=True)

    @staticmethod
    def _create_test_post(user: u.User, is_active: bool) -> "Post":
        post = Post.objects.create(user=user, is_active=is_active)
        PostFile.objects.create(content="tt", post=post)
        return post

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # if self.tags:
            # self.tags.set([user.pk for user in self.tags])


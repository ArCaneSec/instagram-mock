from django.db import models as m

from post import models as p
from user import models as u

# Create your models here.


class CommentLikes(m.Model):
    user = m.ForeignKey(u.User, on_delete=m.CASCADE)
    comment = m.ForeignKey("Comment", on_delete=m.CASCADE)
    date = m.DateTimeField(auto_now_add=True)


class Comment(m.Model):
    user = m.ForeignKey(u.User, on_delete=m.CASCADE)
    post = m.ForeignKey(p.Post, on_delete=m.CASCADE, related_name="comments")
    content = m.TextField()
    created_at = m.DateTimeField(auto_now_add=True)
    updated_at = m.DateTimeField(auto_now=True)
    is_active = m.BooleanField(default=True)
    likes = m.ManyToManyField(
        u.User,
        through=CommentLikes,
        related_name="user_comment_likes",
        blank=True,
    )
    tags = m.ManyToManyField(
        u.User, related_name="user_comment_tags", blank=True
    )

    @property
    def total_likes(self):
        return self.likes.count()
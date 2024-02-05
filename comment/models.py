from django.db import models as m

from post import models as p
from user import models as u

# Create your models here.


class CommentLikes(m.Model):
    user = m.ForeignKey(u.User, on_delete=m.CASCADE)
    comment = m.ForeignKey("Comment", on_delete=m.CASCADE)
    date = m.DateTimeField(auto_now_add=True)


class Comment(m.Model):
    user = m.ForeignKey(u.User, on_delete=m.SET_NULL)
    post = m.ForeignKey(p.Post, on_delete=m.SET_NULL)
    content = m.TextField()
    created_at = m.DateTimeField(auto_now_add=True)
    updated_at = m.DateTimeField(auto_now=True)
    is_active = m.BooleanField(default=True)
    likes = m.ManyToManyField(u.User, through=CommentLikes)
    tags = m.ManyToManyField(u.User)

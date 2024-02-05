from django.db import models as m

# Create your models here.


class BasicUserInfo(m.Model):
    username = m.CharField(max_length=250, unique=True)
    nickname = m.CharField(max_length=250, blank=True, default=username)
    name = m.CharField(max_length=250)
    last_name = m.CharField(max_length=250)
    profile = m.ImageField(upload_to="/static/users/profiles/")
    biography = m.TextField(null=True, blank=True)
    email = m.EmailField(null=True, blank=True)
    phone_number = m.CharField(max_length=11, null=True, blank=True)
    is_active = m.BooleanField(default=False)
    is_deleted = m.BooleanField(default=False)

    class Meta:
        abstract = True


class User(BasicUserInfo):
    is_private = m.BooleanField(default=False)
    password = m.CharField(max_length=250)
    followers = m.ManyToManyField(
        to="self", through="Follows", related_name="following"
    )
    close_friends = m.ManyToManyField(to="self")
    hide_story = m.ManyToManyField(to="self")

    def __str__(self) -> str:
        return "%s %s %s" % super().username, super().name, super().last_name


class Follows(m.Model):
    following = m.ForeignKey(User)
    followers = m.ForeignKey(User)
    date = m.DateTimeField(auto_now_add=True)

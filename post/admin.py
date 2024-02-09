from django.contrib import admin
from .models import Post, PostLikes
# Register your models here.

admin.site.register([Post, PostLikes])

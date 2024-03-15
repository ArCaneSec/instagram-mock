from django.contrib import admin
from .models import Post, PostLikes, PostFile, Hashtag, PostViewsHistory
# Register your models here.

admin.site.register([Post, PostLikes, PostFile, Hashtag, PostViewsHistory])

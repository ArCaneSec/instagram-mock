from django.contrib import admin
from .models import Post, PostLikes, PostFile
# Register your models here.

admin.site.register([Post, PostLikes, PostFile])

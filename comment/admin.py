from django.contrib import admin

from .models import Comment, CommentLikes

# Register your models here.

admin.site.register([Comment, CommentLikes])

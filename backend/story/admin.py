from django.contrib import admin

from .models import Story, StoryViews

# Register your models here.

admin.site.register([Story, StoryViews])

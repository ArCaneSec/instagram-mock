from django.contrib import admin
from .models import User, FollowRequest, Follow

# Register your models here.


admin.site.register([User, FollowRequest, Follow])

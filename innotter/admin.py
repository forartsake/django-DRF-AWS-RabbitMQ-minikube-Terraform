from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from innotter.models import User, Tag, Page, Post

admin.site.register(User)
admin.site.register(Tag)
admin.site.register(Page)
admin.site.register(Post)

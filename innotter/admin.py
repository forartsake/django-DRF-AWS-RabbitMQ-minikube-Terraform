from django.contrib import admin

from innotter.models import User, Page, Post

# Register your models here.
admin.site.register(User)
admin.site.register(Page)
admin.site.register(Post)
from datetime import datetime, timedelta
from django.core.validators import validate_image_file_extension
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from uuid import uuid4


class User(AbstractUser):
    class Roles(models.TextChoices):
        USER = 'user'
        MODERATOR = 'moderator'
        ADMIN = 'admin'

    email = models.EmailField(unique=True)
    image_s3_path = models.CharField(max_length=200, null=True, blank=True)
    role = models.CharField(max_length=9, choices=Roles.choices)
    title = models.CharField(max_length=80)
    is_blocked = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, blank=True, related_name='user_groups')
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='user_permissions',
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)


def page_directory_path(instance, filename):
    page_id = instance.id
    current_date = datetime.now().strftime('%Y-%m-%d')
    return f"pages/{page_id}/{current_date}/{filename}"


class Page(models.Model):
    name = models.CharField(max_length=80)
    uuid = models.CharField(max_length=50, unique=True, default=uuid4, editable=False)  # instead of pk / uuid
    description = models.TextField()
    tags = models.ManyToManyField('innotter.Tag', related_name='pages', blank=True)
    owner = models.ForeignKey('innotter.User', on_delete=models.CASCADE, related_name='pages')
    followers = models.ManyToManyField('innotter.User', related_name='follows', blank=True)
    image = models.ImageField(upload_to=page_directory_path, validators=[validate_image_file_extension])
    is_private = models.BooleanField(default=False)
    follow_requests = models.ManyToManyField('innotter.User', related_name='requests', blank=True)
    unblock_date = models.DateTimeField(null=True, blank=True)
    is_blocked = models.BooleanField(default=False)


class Post(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='posts')
    content = models.CharField(max_length=180)
    reply_to = models.ForeignKey('innotter.Post', on_delete=models.SET_NULL, null=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField('innotter.User', related_name='liked_posts', null=True)

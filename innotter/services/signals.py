import json

from django.db.models import Count
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from innotter.models import User, Page, Post
from innotter.services.rabbitmq_producer import ProducerClient
from innotter.tasks import celery_send_email_to_followers


@receiver(post_save, sender=User)
def block_user_pages(sender, instance, **kwargs):
    pages = Page.objects.filter(owner=instance)
    for page in pages:
        if instance.is_blocked:
            page.is_blocked = True
            page.save()
        else:
            page.is_blocked = False
            page.save()


@receiver(post_save, sender=Post)
def new_post_notification(sender, instance, created, **kwargs):
    if created:
        followers = instance.page.followers.all()
        post_dict = {
            "pk": instance.pk,
            "content": instance.content,
            "page_owner_username": instance.page.owner.username,
            "page_id": instance.page.id,
            "post_id": instance.id
        }

        for follower in followers:
            follower_dict = {
                "username": follower.username,
                "email": follower.email
            }
            celery_send_email_to_followers.delay(post_dict, follower_dict)


@receiver(post_save, sender=Page)
def new_page_created(sender, instance, created, **kwargs):
    if created:
        body = {'user_id': instance.owner.id,
                'page_id': instance.id,
                'posts_count': 0,
                'followers_count': 0,
                'likes_count': 0}
        ProducerClient.send_message(json.dumps(body))


@receiver(post_save, sender=Post)
def new_post_created(sender, instance, created, **kwargs):
    page = Page.objects.get(id=instance.page.id)
    posts = page.posts.count()

    body = {'user_id': instance.page.owner.id,
            'page_id': instance.page.id,
            'posts_count': posts,
            }
    ProducerClient.send_message(json.dumps(body))


@receiver(m2m_changed, sender=Post.likes.through)
def update_page_likes(sender, instance, action, **kwargs):
    if action == "post_add" or action == "post_remove":
        page = instance.page

        total_likes = page.posts.all().aggregate(total_likes=Count('likes'))['total_likes']
        body = {'user_id': instance.page.owner.id,
                'page_id': instance.page.id,
                'likes_count': total_likes,
                }
        ProducerClient.send_message(json.dumps(body))


@receiver(m2m_changed, sender=Page.followers.through)
def update_page_followers(sender, instance, action, **kwargs):
    if action == "post_add" or action == "post_remove":
        total_followers = instance.followers.count()

        body = {'user_id': instance.owner.id,
                'page_id': instance.id,
                'followers_count': total_followers,
                }
        ProducerClient.send_message(json.dumps(body))

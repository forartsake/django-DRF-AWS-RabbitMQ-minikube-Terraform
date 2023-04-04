from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from innotter.models import User, Page, Post
from innotter.tasks import celery_send_email_to_followers, celery_unblock_page


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



from innotter.services.services import NotificationService, PageService
from celery import shared_task


@shared_task
def celery_send_email_to_followers(post_dict, followers_dict):
    NotificationService.send_to_follower(post_dict, followers_dict)


@shared_task
def celery_unblock_page():
    PageService.unblock_page()
    return "Page has been unblocked"

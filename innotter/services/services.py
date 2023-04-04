import os
from datetime import datetime, timedelta

import jwt
from django.utils.timezone import make_naive
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from innotter.models import Page, User, Post, Tag
from innotter.serializers import PostSerializer, CreateTagSerializer

from django.core.mail import send_mail
from django.contrib.auth import authenticate


class UserService:

    @staticmethod
    def get_liked_posts_by_user(user_id):
        return Post.objects.filter(likes=user_id)

    @staticmethod
    def get_news_posts(user):
        followed_pages = user.follows.all()
        own_pages = user.pages.all()
        all_posts = Post.objects.filter(Q(page__in=followed_pages) | Q(page__in=own_pages))
        news_posts = all_posts.order_by('-created_at')
        return news_posts


class AuthService:

    @staticmethod
    def create_token(username, password):
        user = authenticate(username=username, password=password)
        if user:
            expiration_delta = int(os.getenv('WT_EXPIRATION_DELTA'))
            exp = (datetime.now() + timedelta(seconds=expiration_delta)).timestamp()
            payload = {'user_id': user.id, 'exp': exp}
            secret_key = os.getenv('SECRET_KEY')
            token = jwt.encode(payload, secret_key, algorithm='HS256')
            return token
        else:
            return None


class PageService:

    @staticmethod
    def add_tag_to_page(page, tag_names):
        tags = []
        for tag_name in tag_names:
            tag_obj, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                tag_serializer = CreateTagSerializer(data={'name': tag_name})
                tag_serializer.is_valid(raise_exception=True)
                tag_obj = tag_serializer.save()
            tags.append(tag_obj)
        if tags:
            page.tags.add(*tags)
            page.save()

    @staticmethod
    def remove_tags_from_page(page, tags):
        for tag_name in tags:
            try:
                tag_obj = Tag.objects.get(name=tag_name)
                print(f"tag_obj {tag_obj}")

                page.tags.remove(tag_obj)
            except Tag.DoesNotExist:
                pass
        page.save()

    @staticmethod
    def follow_or_unfollow(user_id, page_id, is_accept):
        try:
            user = User.objects.get(id=user_id)
            page = Page.objects.get(id=page_id)

            if is_accept:
                if page.followers.filter(id=user_id).exists():
                    return False, 'Your subscription request has already been sent'
                if page.owner == user:
                    return False, 'You cannot subscribe to yourself'
                if page.is_private:
                    page.follow_requests.add(user)
                    return True, 'Follow request has been sent'
                else:
                    page.followers.add(user)
                    return True, 'You have subscribed to the page'
            else:
                if page.followers.remove(user):
                    return True, 'You have unsubscribed from the page'
                if page.is_private:
                    page.follow_requests.remove(user)
                    return True, 'Your follow request has been canceled'
                else:
                    return False, 'You have not subscribed to the page'
        except ObjectDoesNotExist:
            return False, 'User/page does not exist'

    @staticmethod
    def accept_or_reject_follow_request(page, user, request_user_ids, flag):

        if page.owner == user:
            for user_id in request_user_ids:
                if not flag:
                    page.follow_requests.remove(user_id)
                    return True, 'request has been disapproved successfully'
                else:
                    page.followers.add(user_id)
                    page.follow_requests.remove(user_id)
                    return True, "User request has been approved successfully"
        return False, 'You are not allowed to perform this action'

    @staticmethod
    def unblock_page():
        blocked_pages = Page.objects.filter(is_blocked=True)
        if blocked_pages:
            for page in blocked_pages:
                if timezone.now().strftime("%Y-%m-%d %H:%M:%S") >= page.unblock_date.strftime("%Y-%m-%d %H:%M:%S"):
                    page.is_blocked = False
                    print(f"unblock date before {page.unblock_date}")
                    page.unblock_date = None
                    print(f"unblock date after {page.unblock_date}")
                    page.save()
                    return (
                        f"Page {page.pk} that belongs to {page.owner} has been unblocked",
                        status.HTTP_200_OK
                    )


class PostService:
    def create_post(self, user, page_id, data):
        page = get_object_or_404(Page, id=page_id)
        if page.owner != user:
            raise PermissionDenied("You don't have permission to create posts for this page.")
        serializer = PostSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(page=page)
        return post

    def update_post(self, user, post_id, data):
        post = get_object_or_404(Post, id=post_id)
        if post.page.owner != user:
            raise PermissionDenied("You don't have permission to update this post.")
        serializer = PostSerializer(instance=post, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        return post

    def delete_post(self, user, post_id):
        print(f'delete_post:')
        post = get_object_or_404(Post, id=post_id)
        if user.role not in ('admin', 'moderator') and post.page.owner != user:
            raise PermissionDenied("You don't have permission to delete this post.")
        post.delete()

    def like_post(self, user, post_id):
        post = get_object_or_404(Post, pk=post_id)
        if post.page.owner == user:
            raise PermissionDenied("You cannot like a post that you own")
        post.likes.add(user)
        post.save()

    def unlike_post(self, user, post_id):
        post = get_object_or_404(Post, pk=post_id)
        if user not in post.likes.all():
            raise PermissionDenied("You cannot unlike someone else's post")
        post.likes.remove(user)
        post.save()


class NotificationService:
    email_subject = "Dear {}!"
    email_body = """
    We've glad to inform you that {} just published a new post!
    What does he write about? {}
    Check it out more at http://127.0.0.1:8000/pages/{}/posts/{}/
    
    """
    from_email = 'thebestoneatwork@gmail.com'

    @classmethod
    def send_to_follower(cls, post_dict, followers_dict):
        send_mail(
            subject=cls.email_subject.format(followers_dict['username']),
            message=cls.email_body.format(
                post_dict['page_owner_username'],
                post_dict['content'],
                post_dict['page_id'],
                post_dict['post_id']
            ),
            from_email=cls.from_email,
            recipient_list=[followers_dict['email']],
        )

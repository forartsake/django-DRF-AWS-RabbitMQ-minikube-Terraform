import os
from datetime import datetime, timedelta

import jwt
import requests

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, serializers
from rest_framework.response import Response

from innotter.models import Page, User, Post, Tag
from innotter.serializers import PostContentSerializer, CreatePostSerializer

from django.core.mail import send_mail
from django.contrib.auth import authenticate


class UserService:

    @staticmethod
    def get_liked_posts_by_user(user_id):
        likes = Post.objects.filter(likes=user_id)
        return likes

    @staticmethod
    def get_news_posts(user):
        followed_pages = user.follows.all()
        own_pages = user.pages.all()
        all_posts = Post.objects.filter(Q(page__in=followed_pages) | Q(page__in=own_pages))
        news_posts = all_posts.order_by('-created_at')
        if news_posts.exists():
            serializer = PostContentSerializer(news_posts, many=True)
            return serializer.data
        else:
            return 'There is no news yet.'


class AuthService:

    @staticmethod
    def create_token(username, password):
        user = authenticate(username=username, password=password)
        if user:
            expiration_delta = int(os.getenv('WT_EXPIRATION_DELTA'))
            exp = (datetime.now() + timedelta(seconds=expiration_delta)).timestamp()
            payload = {'user_id': user.id, 'exp': exp, 'username': username}
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
                tags.append(tag_obj)
            tags.append(tag_obj)
        if tags:
            page.tags.add(*tags)
            page.save()

    @staticmethod
    def remove_tags_from_page(page, tags):
        for tag_name in tags:
            try:
                tag_obj = Tag.objects.get(name=tag_name)

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
                    page.save()
                    return True, 'Follow request has been sent'
                else:
                    page.followers.add(user)
                    page.save()

                    return True, 'You have subscribed to the page'
            else:

                if page.followers.filter(pk=user_id).exists():  # added instead of get/ filter and at the end.exists()

                    page.followers.remove(user)
                    page.save()
                    return True, 'You have unsubscribed from the page'

                if page.follow_requests.get(pk=user_id) in page.follow_requests.all():

                    page.follow_requests.remove(user)
                    page.save()
                    return True, 'Your follow request has been canceled'
                else:
                    return False, 'You have not subscribed to the page'

        except ObjectDoesNotExist:
            return False, 'User/page does not exist'

    @staticmethod
    def accept_or_reject_follow_request(page, user, request_user_ids, flag):

        if page.owner == user and page.owner.pk not in request_user_ids:
            for user_id in request_user_ids:
                if not flag:
                    page.follow_requests.remove(user_id)
                    page.save()
                    return True, 'request has been disapproved successfully'
                else:
                    page.followers.add(user_id)
                    page.follow_requests.remove(user_id)
                    page.save()
                    return True, "User request has been approved successfully"
        return False, 'You are not allowed to perform this action'

    @staticmethod
    def unblock_page():
        blocked_pages = Page.objects.filter(is_blocked=True)
        if blocked_pages:
            for page in blocked_pages:
                if timezone.now().strftime("%Y-%m-%d %H:%M:%S") >= page.unblock_date.strftime("%Y-%m-%d %H:%M:%S"):
                    page.is_blocked = False
                    page.unblock_date = None
                    page.save()
                    return (
                        f"Page {page.pk} that belongs to {page.owner} has been unblocked",
                        status.HTTP_200_OK
                    )


class PostService:
    @staticmethod
    def create_post(page, user, data):

        if page.owner != user:
            return Response({'status': "You don't have permission to create posts for this page."},
                            status=403)
        serializer = CreatePostSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(page=page)
        return post

    @staticmethod
    def like_post(user, post_id):
        post = get_object_or_404(Post, pk=post_id)
        if post.page.owner == user:
            return False, "You cannot like a post that you own."
        post.likes.add(user)
        post.save()
        return True, "Post has been liked successfully."

    @staticmethod
    def unlike_post(user, post_id):
        post = get_object_or_404(Post, pk=post_id)
        if user not in post.likes.all():
            return False, "You cannot unlike someone else's post."
        post.likes.remove(user)
        post.save()
        return True, "Post has been unliked successfully."


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

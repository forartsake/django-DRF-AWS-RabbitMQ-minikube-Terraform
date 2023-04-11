import pytest
from django.urls import reverse
from innotter.models import Page, User, Post, Tag


@pytest.mark.django_db(transaction=True)
def test_create_post_using_endpoint(client, page_02_with_tags_owner_is_user_02, user_2):
    page = page_02_with_tags_owner_is_user_02

    url = f'/pages/{page.pk}/create_post/'

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_2['token']}"
    response = client.post(url, {'content': 'Bruh'}, content_type='application/json')
    assert Post.objects.filter(id=response.data['id']).exists()
    assert response.status_code == 201


@pytest.mark.django_db(transaction=True)
def test_create_post(client, page_02_with_tags_owner_is_user_02, user_2):
    page = page_02_with_tags_owner_is_user_02
    url = reverse('posts-list')
    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_2['token']}"
    response = client.post(url, {'page': page.pk, 'content': 'test-test-test'}, content_type='application/json')
    assert Post.objects.filter(id=response.data['id']).exists()
    assert response.status_code == 201


@pytest.mark.django_db(transaction=True)
def test_edit_post(client, post_on_page_owner_is_user_2, user_2):
    post = post_on_page_owner_is_user_2

    url = reverse('posts-detail', kwargs={"pk": post.pk})

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_2['token']}"
    response = client.patch(url, {'page': post.page.pk, 'content': 'EDITED CONTENT'}, content_type='application/json')
    assert post.content != response.data['content']
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_edit_post_by_different_user(client, post_on_page_owner_is_user_2, user_1):
    post = post_on_page_owner_is_user_2
    url = reverse('posts-detail', kwargs={"pk": post.pk})
    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_1['token']}"
    response = client.patch(url, {'page': post.page.pk, 'content': 'EDITED CONTENT'}, content_type='application/json')

    assert response.status_code == 403


@pytest.mark.django_db(transaction=True)
def test_post_like(client, post_on_page_owner_is_user_2, user_1, user_2):
    page = post_on_page_owner_is_user_2.page
    post = post_on_page_owner_is_user_2
    url = f"http://127.0.0.1:8000/pages/{page.id}/posts/{post.id}/like/"

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_1['token']}"
    response = client.generic('POST', url, data={'post_id': post.id, 'page_id': page.id},
                              content_type='application/json')

    assert response.status_code == 200
    assert post.likes.all().count() == 1


@pytest.mark.django_db(transaction=True)
def test_post_like_by_onwer(client, post_on_page_owner_is_user_2, user_2):
    page = post_on_page_owner_is_user_2.page
    post = post_on_page_owner_is_user_2
    url = f"http://127.0.0.1:8000/pages/{page.id}/posts/{post.id}/like/"

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_2['token']}"
    response = client.generic('POST', url, data={'post_id': post.id, 'page_id': page.id},
                              content_type='application/json')

    assert response.status_code == 403
    assert post.likes.all().count() == 0


@pytest.mark.django_db(transaction=True)
def test_post_unlike(client, post_on_page_owner_is_user_2, user_1, user_2):
    post = post_on_page_owner_is_user_2
    post.likes.add(user_2['user'])
    post.save()
    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_2['token']}"
    url = f"http://127.0.0.1:8000/pages/{post.page.id}/posts/{post.id}/unlike/"
    response = client.generic('POST', url, data={'post_id': post.id, 'page_id': post.page.id},
                              content_type='application/json')
    assert response.status_code == 200
    assert post.likes.all().count() == 0


@pytest.mark.django_db(transaction=True)
def test_post_unlike_by_different_user(client, post_on_page_owner_is_user_2, user_1, user_2):
    post = post_on_page_owner_is_user_2
    post.likes.add(user_2['user'])
    post.save()
    url = f"http://127.0.0.1:8000/pages/{post.page.id}/posts/{post.id}/unlike/"
    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_1['token']}"

    response = client.generic('POST', url, data={'post_id': post.id, 'page_id': post.page.id},
                              content_type='application/json')

    assert response.status_code == 400
    assert post.likes.all().count() == 1


@pytest.mark.django_db(transaction=True)
def test_post_delete_by_owner(client, post_on_page_owner_is_user_2, user_1, user_2):
    post = post_on_page_owner_is_user_2
    url = f"http://127.0.0.1:8000/pages/{post.page.id}/posts/{post.id}/"
    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_2['token']}"
    response = client.generic('DELETE', url, content_type='application/json')

    assert response.status_code == 204
    assert not Post.objects.filter(id=post.id).exists()


@pytest.mark.django_db(transaction=True)
def test_post_delete_by_other(client, post_on_page_owner_is_user_2, user_1, user_2):
    post = post_on_page_owner_is_user_2
    url = f"http://127.0.0.1:8000/pages/{post.page.id}/posts/{post.id}/"
    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_1['token']}"
    response = client.generic('DELETE', url, content_type='application/json')
    assert response.status_code == 403
    assert Post.objects.filter(id=post.id).exists()


@pytest.mark.django_db(transaction=True)
def test_post_reply(client, user_1, user_2):
    page_1 = Page.objects.create(name="TEST TITLE", description="TEST DESCRIPTION", owner=user_1['user'])
    post_from_reply = Post.objects.create(page=page_1, content='Test')

    page_2 = Page.objects.create(name="TEST TITLE", description="TEST DESCRIPTION", owner=user_2['user'])
    post_to_be_replied = Post.objects.create(page=page_1, content='Test REPLY')

    url = reverse('posts-reply', kwargs={"pk": post_to_be_replied.id})

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_1['token']}"
    response = client.post(url, {'page_id': page_2.pk, 'content': 'Reply content'}, content_type='application/json')
    post_from_reply.refresh_from_db()

    assert response.status_code == 200
    assert response.data['reply_to'] == post_to_be_replied.id

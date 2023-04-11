import pytest
from django.urls import reverse
from innotter.models import Page, User, Post, Tag

pytest_plugins = ['django']


@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpass1235!xsf',
        "role": "user",
        "title": "casual_user"
    }


@pytest.fixture
def negative_user_data():
    return {
        'username': 'test',
        'email': 'testuserexample.com',
        'password': 'testpass1235!xsf',
    }


@pytest.fixture
def create_user_1():
    user = User.objects.create(username='created_test_user',
                               email='test_user_1@gmail.com',
                               role='user',
                               title='casual_1'
                               )
    user.set_password('testpassword12!cx')
    user.save()
    return user


@pytest.fixture
def user_1(client):
    user = User.objects.create(username='test_user_1',
                               email='test_user_1@gmail.com',
                               role='user',
                               title='casual_1'
                               )
    user.set_password('testpassword12!cx')
    user.save()
    url = reverse('users-login')
    response = client.post(url, {'username': 'test_user_1', 'password': 'testpassword12!cx'}).json()
    return {'user': user, 'token': response['token']}


@pytest.fixture
def user_2(client):
    user = User.objects.create(username='test_user_2',
                               email='test_user_2@gmail.com',
                               role='user',
                               title='casual_2',
                               is_blocked=True,
                               )
    user.set_password('testpassword12!cx')
    user.save()
    url = reverse('users-login')
    response = client.post(url, {'username': 'test_user_2', 'password': 'testpassword12!cx'}).json()
    return {'user': user, 'token': response['token']}


@pytest.fixture
def admin_user(client):
    user = User.objects.create(username='test_admin',
                               email='test_admin@gmail.com',
                               role='admin',
                               title='casual'
                               )
    user.set_password('adminuser098!cx')
    user.save()
    url = reverse('users-login')
    response = client.post(url, {'username': 'test_admin', 'password': 'adminuser098!cx'}).json()

    return {'admin': user, 'token': response['token']}


@pytest.fixture
def admin_user_01(client):
    user = User.objects.create(username='test_admin_01',
                               email='test_admin_01@gmail.com',
                               role='admin',
                               title='casual'
                               )
    user.set_password('adminuser098!cx')
    user.save()
    url = reverse('users-login')
    response = client.post(url, {'username': 'test_admin_01', 'password': 'adminuser098!cx'}).json()

    return {'admin': user, 'token': response['token']}


@pytest.fixture
def page_data():
    return {'name': "TestPageName",
            'description': "Here you may see an useful description"
            }


@pytest.fixture
def page_data_2():
    return {'name': "TestPageNameNumber2",
            'description': "Here you may see an unuseful description"
            }


@pytest.fixture
def page_with_tags_owner_is_user_1(client, user_1, page_data):
    tag_1 = Tag.objects.create(name='test_tag_1')
    tag_2 = Tag.objects.create(name='test_tag_2')
    tag_3 = Tag.objects.create(name='test_tag_3')

    url = reverse('pages-list')

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_1['token']}"
    tags_field = {'tags': [tag_1.pk, tag_2.pk, tag_3.pk]}

    page_data.update(tags_field)

    response = client.post(url, page_data, content_type='application/json')

    page = Page.objects.get(uuid=response.data['uuid'])

    return page


@pytest.fixture
def page_02_with_tags_owner_is_user_02(user_2):
    tag_1 = Tag.objects.create(name='test_tag_10')
    tag_2 = Tag.objects.create(name='test_tag_20')
    tag_3 = Tag.objects.create(name='test_tag_30')

    page = Page.objects.create(
        name="Page created by user 04",
        description="Better Call Soul",
        owner=user_2['user']
    )
    page.tags.set([tag_1, tag_2, tag_3])
    return page


@pytest.fixture
def page_01_without_tags_owner_is_user_01(user_1):
    page = Page.objects.create(
        name=f"Page created by user {user_1['user'].username}",
        description="Breaking Bad",
        owner=user_1['user']
    )
    return page


@pytest.fixture
def subscribed_page_owner_is_user_2(client, user_1, page_02_with_tags_owner_is_user_02):
    page = page_02_with_tags_owner_is_user_02

    url = f'/pages/{page.pk}/subscribe_or_unsubscribe/'

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_1['token']}"

    response = client.post(url, {'user_id': user_1['user'].pk, 'flag': True}, content_type='application/json')
    page.refresh_from_db()

    return {'page': page, 'response': response}


@pytest.fixture
def private_page_owner_is_user_2(user_2):
    tag_1 = Tag.objects.create(name='test_tag_10')
    tag_2 = Tag.objects.create(name='test_tag_20')
    tag_3 = Tag.objects.create(name='test_tag_30')

    page = Page.objects.create(
        name="Page created by user 04",
        description="Better Call Soul",
        owner=user_2['user'],
        is_private=True
    )
    page.tags.set([tag_1, tag_2, tag_3])
    return page


@pytest.fixture
def private_page_with_follow_request_by_user1_owner_is_user_2(client, user_1, private_page_owner_is_user_2):
    page = private_page_owner_is_user_2

    url = f'/pages/{page.pk}/subscribe_or_unsubscribe/'

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_1['token']}"

    response = client.post(url, {'user_id': user_1['user'].pk, 'flag': True}, content_type='application/json')
    page.refresh_from_db()

    return {'page': page, 'response': response}


@pytest.fixture()
def post_on_page_owner_is_user_2(client, page_02_with_tags_owner_is_user_02, user_2):
    page = page_02_with_tags_owner_is_user_02
    url = reverse('posts-list')
    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_2['token']}"
    response = client.post(url, {'page': page.pk, 'content': 'test-test-test'}, content_type='application/json')
    post = Post.objects.get(id=response.data['id'])
    return post

import pytest
from django.urls import reverse
from innotter.models import Page, Tag


@pytest.mark.django_db(transaction=True)
def test_create_page_required_fields(client, page_data, user_1):
    """
    Testing the creation of a page with required fields by an authenticated user.

    :param client: django testing client
    :param page_data: a dictionary with page data that contains required fields for creating pages.
    :param user_1: a dictionary with user authentication data
    :return: None
    """
    url = reverse('pages-list')

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_1['token']}"

    response = client.post(url, page_data, content_type='application/json')
    created_page = Page.objects.get(uuid=response.data['uuid'])

    assert Page.objects.count() == 1
    assert created_page.name == page_data['name']
    assert created_page.description == page_data['description']
    assert created_page.owner.username == user_1['user'].username

    assert response.status_code == 201


@pytest.mark.django_db(transaction=True)
def test_create_page_additional_fields(client, page_data, user_1):
    """
    Testing the creation of a page with the initial presence of tags by an authenticated user.

    :param client: django testing client
    :param page_data: a dictionary with page data that contains required fields for creating pages.
    :param user_1: a dictionary with user authentication data
    :return:
    """

    tag_1 = Tag.objects.create(name='test_tag_1')
    tag_2 = Tag.objects.create(name='test_tag_2')
    tag_3 = Tag.objects.create(name='test_tag_3')

    url = reverse('pages-list')

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_1['token']}"

    additional_field = {'tags': [tag_1.pk, tag_2.pk, tag_3.pk]}
    page_data.update(additional_field)

    response = client.post(url, page_data, content_type='application/json')

    created_page = Page.objects.get(uuid=response.data['uuid'])

    tags = created_page.tags.all()

    assert Page.objects.count() == 1
    assert created_page.name == page_data['name']
    assert created_page.description == page_data['description']
    assert created_page.owner.username == user_1['user'].username
    assert tags.count() == len(additional_field['tags'])


@pytest.mark.django_db(transaction=True)
def test_create_page_anonymously(client, page_data):
    url = reverse('pages-list')
    response = client.post(url, page_data, content_type='application/json')

    assert response.status_code == 403


@pytest.mark.django_db(transaction=True)
def test_page_update_method_admin_permission(client, admin_user_01, page_with_tags_owner_is_user_1):
    page = page_with_tags_owner_is_user_1

    url = reverse("pages-detail", kwargs={"pk": page.pk})

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {admin_user_01['token']}"
    response_1 = client.patch(url, {'is_blocked': True}, content_type='application/json')
    response_2 = client.patch(url, {'name': 'updated_name_page'}, content_type='application/json')
    page.refresh_from_db()

    assert response_1.status_code == 200
    assert page.is_blocked

    assert response_2.status_code == 403
    assert page.name != 'updated_name_page'


@pytest.mark.django_db(transaction=True)
@pytest.mark.xfail(reason="Test crashes when run along with others")
def test_page_update_method_owner_permission(client, user_2, page_02_with_tags_owner_is_user_02):
    page = page_02_with_tags_owner_is_user_02

    url = reverse("pages-detail", kwargs={"pk": page.pk})

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_2['token']}"
    response_1 = client.patch(url, {'is_blocked': True}, content_type='application/json')
    response_2 = client.patch(url, {'name': 'updated_name_page'}, content_type='application/json')
    page.refresh_from_db()

    assert response_1.status_code == 403
    assert not page.is_blocked
    assert response_2.status_code == 200
    assert page.name == 'updated_name_page'


@pytest.mark.django_db
def test_page_delete_method_owner(client, user_2, page_02_with_tags_owner_is_user_02):
    page = page_02_with_tags_owner_is_user_02
    url = reverse("pages-detail", kwargs={"pk": page.pk})

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_2['token']}"
    response = client.delete(url, content_type='application/json')

    assert response.status_code == 204
    assert not Page.objects.filter(pk=page.pk).exists()


@pytest.mark.django_db(transaction=True)
def test_adding_tags_to_the_page(client, user_1, page_01_without_tags_owner_is_user_01):
    page = page_01_without_tags_owner_is_user_01

    url = f"http://127.0.0.1:8000/pages/{page.pk}/modify_tag/"
    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_1['token']}"
    data = [
        {"name": "t1"},
        {"name": "t2"}
    ]
    for tag_data in data:
        response = client.post(url, [tag_data], content_type='application/json')
        page.refresh_from_db()
        assert response.status_code == 200
    page.refresh_from_db()
    assert len(page.tags.all()) == len(data)


@pytest.mark.django_db(transaction=True)
def test_removing_tags_from_the_page(client, user_1, page_with_tags_owner_is_user_1):
    page = Page.objects.create(
        name=f"TEST PAGE {user_1['user'].username}",
        description="TEST",
        owner=user_1['user']
    )

    url = f'/pages/{page.id}/modify_tag/'

    tags_to_delete_from_the_page = [
        {"name": "test_tag_1"},
        {"name": "test_tag_2"}
    ]

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_1['token']}"

    response = client.delete(url, tags_to_delete_from_the_page, content_type='application/json')

    assert response.status_code == 200
    assert page.tags.filter(name="test_tag_1").count() == 0
    assert page.tags.filter(name="test_tag_2").count() == 0
    assert len(Tag.objects.all()) == 3


@pytest.mark.django_db(transaction=True)
def test_subscribe_to_the_page(subscribed_page_owner_is_user_2, user_1):
    response = subscribed_page_owner_is_user_2['response']
    page = subscribed_page_owner_is_user_2['page']

    assert response.status_code == 200
    assert page.followers.get(pk=user_1['user'].pk).pk == user_1['user'].pk


@pytest.mark.django_db(transaction=True)
def test_unsubscribe_from_the_page(client, subscribed_page_owner_is_user_2, user_1):
    page = subscribed_page_owner_is_user_2['page']
    url = f'/pages/{page.pk}/subscribe_or_unsubscribe/'

    response = client.post(url, {'user_id': user_1['user'].pk, 'flag': False}, content_type='application/json')
    page.refresh_from_db()

    assert response.status_code == 200
    assert page.followers.filter(pk=user_1['user'].pk).count() == 0


@pytest.mark.django_db(transaction=True)
def test_subscribe_to_the_private_page(client, private_page_owner_is_user_2, user_1):
    page = private_page_owner_is_user_2
    url = f'/pages/{page.pk}/subscribe_or_unsubscribe/'

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_1['token']}"
    response = client.post(url, {'user_id': user_1['user'].pk, 'flag': True}, content_type='application/json')
    page.refresh_from_db()
    assert response.status_code == 200
    assert page.follow_requests.get(pk=user_1['user'].pk).pk == user_1['user'].pk


@pytest.mark.django_db(transaction=True)
def test_deny_follow_request_from_the_private_page(client, private_page_with_follow_request_by_user1_owner_is_user_2,
                                                   user_1):
    page = private_page_with_follow_request_by_user1_owner_is_user_2['page']
    url = f'/pages/{page.pk}/subscribe_or_unsubscribe/'

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_1['token']}"

    response = client.post(url, {'user_id': user_1['user'].pk, 'flag': False}, content_type='application/json')
    page.refresh_from_db()

    assert page.follow_requests.all().count() == 0
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_accept_follow_request(client, private_page_with_follow_request_by_user1_owner_is_user_2, user_2, user_1):
    page = private_page_with_follow_request_by_user1_owner_is_user_2['page']
    url = f'/pages/{page.pk}/accept_or_reject_subscription/'
    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_2['token']}"
    response = client.post(url, {'user_ids': [user_1['user'].pk], 'flag': True}, content_type='application/json')
    page.refresh_from_db()
    assert response.status_code == 200
    assert page.follow_requests.all().count() == 0
    assert page.followers.all().count() == 1


@pytest.mark.django_db(transaction=True)
def test_reject_follow_request(client, private_page_with_follow_request_by_user1_owner_is_user_2, user_2, user_1):
    page = private_page_with_follow_request_by_user1_owner_is_user_2['page']
    url = f'/pages/{page.pk}/accept_or_reject_subscription/'
    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_2['token']}"

    response = client.post(url, {'user_ids': [user_1['user'].pk], 'flag': False}, content_type='application/json')
    page.refresh_from_db()

    assert response.status_code == 200
    assert page.follow_requests.all().count() == 0
    assert page.followers.all().count() == 0


@pytest.mark.django_db(transaction=True)
def test_follow_requests_list(client, private_page_with_follow_request_by_user1_owner_is_user_2, user_2, user_1):
    page = private_page_with_follow_request_by_user1_owner_is_user_2['page']
    url = f'/pages/{page.pk}/follow_requests_list/'

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_2['token']}"
    response = client.get(url, content_type='application/json')

    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db(transaction=True)
def test_followers_list(client, subscribed_page_owner_is_user_2, user_1):
    page = subscribed_page_owner_is_user_2['page']
    url = f'/pages/{page.pk}/followers_list/'

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_1['token']}"
    response = client.get(url, content_type='application/json')

    assert response.status_code == 200
    assert len(response.data) == 1

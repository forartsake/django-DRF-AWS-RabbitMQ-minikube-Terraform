import pytest
from innotter.models import User


@pytest.mark.django_db(transaction=True)
def test_search_user(client, post_on_page_owner_is_user_2, page_with_tags_owner_is_user_1, user_1):
    user1 = User.objects.create(username='John', email='user1@example.com', password='user1password')
    user2 = User.objects.create(username='Tony', email='user2@example.com', password='user2password')
    user3 = User.objects.create(username='Anthony', email='user3@example.com', password='user3password')
    user1.save()
    user2.save()
    user3.save()
    url = '/search/'
    search_query = 'Jo'
    search_type = 'user'
    response = client.get(url, {'search': search_query, 'type': search_type})
    data = response.json()
    assert len(data) == 1
    assert data[0]['username'] == user1.username


@pytest.mark.django_db(transaction=True)
def test_search_page(client, page_with_tags_owner_is_user_1, user_1):
    page = page_with_tags_owner_is_user_1

    url = '/search/'
    search_query = 'P'
    search_type = 'page'
    response = client.get(url, {'search': search_query, 'type': search_type})
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == page.name

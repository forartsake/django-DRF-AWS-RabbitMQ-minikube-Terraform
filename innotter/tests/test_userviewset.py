import pytest
from django.urls import reverse
from innotter.models import Page, User, Post, Tag


@pytest.mark.django_db
def test_user_registration(client, user_data):
    url = reverse('users-register')
    response = client.post(url, user_data)
    user = User.objects.get(username='testuser')
    assert user is not None
    assert response.status_code == 201
    assert 'username' in response.data
    assert 'email' in response.data


@pytest.mark.django_db
def test_negative_user_registration(client, negative_user_data):
    url = reverse('users-register')
    response = client.post(url, negative_user_data)
    with pytest.raises(User.DoesNotExist):
        User.objects.get(username='test')
    assert response.status_code == 400


@pytest.mark.django_db
def test_user_login(client, create_user_1):
    url = reverse('users-login')
    user = create_user_1
    data = {
        'username': user.username,
        'password': 'testpassword12!cx'
    }
    response = client.post(url, data)
    assert response.status_code == 200
    assert 'token' in response.data


@pytest.mark.django_db
def test_user_update_method_admin_permission(client, admin_user, user_1, user_2):
    url_user_1 = reverse("users-detail", kwargs={"pk": user_1["user"].pk})
    url_user_2 = reverse("users-detail", kwargs={"pk": user_2["user"].pk})

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {admin_user['token']}"

    response_1 = client.patch(url_user_1, {'is_blocked': True}, content_type='application/json')
    response_2 = client.patch(url_user_2, {'username': 'changedname'}, content_type='application/json')
    user_1['user'].refresh_from_db()

    assert response_1.status_code == 200
    assert user_1['user'].is_blocked

    assert user_2['user'].username != 'changedname'
    assert response_2.status_code == 403


@pytest.mark.django_db
def test_user_update_method_owner_permission(client, user_1):
    url = reverse("users-detail", kwargs={"pk": user_1["user"].pk})
    username_before_changes = user_1['user'].username

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_1['token']}"
    response_1 = client.patch(url, {'username': 'changednamed'}, content_type='application/json')
    response_2 = client.patch(url, {'is_blocked': True}, content_type='application/json')
    user_1['user'].refresh_from_db()

    assert response_1.status_code == 200
    assert response_1.data['username'] != username_before_changes

    assert response_2.status_code == 403


@pytest.mark.django_db
def test_user_update_method_casual_user_permission(client, user_1, user_2):
    url = reverse("users-detail", kwargs={"pk": user_1["user"].pk})

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_2['token']}"

    response_1 = client.patch(url, {'username': 'changednamed'}, content_type='application/json')
    response_2 = client.patch(url, {'is_blocked': True}, content_type='application/json')
    user_1['user'].refresh_from_db()

    assert response_1.status_code == 403
    assert response_2.status_code == 403


@pytest.mark.django_db
def test_anonymous_user_update_method(client, user_1):
    url = reverse("users-detail", kwargs={"pk": user_1["user"].pk})
    response = client.patch(url, {'username': 'changednamed'}, content_type='application/json')
    user_1['user'].refresh_from_db()

    assert response.status_code == 403


@pytest.mark.django_db
def test_user_destroy_method_admin_permission(client, admin_user, user_1):
    url = reverse("users-detail", kwargs={"pk": user_1["user"].pk})

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {admin_user['token']}"
    response = client.delete(url)

    user_exists = User.objects.filter(pk=user_1["user"].pk).exists()

    assert response.status_code == 405
    assert user_exists


@pytest.mark.django_db
def test_user_destroy_method_casual_user_permission(client, user_1, user_2):
    url = reverse("users-detail", kwargs={"pk": user_1["user"].pk})

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_2['token']}"
    response = client.delete(url)

    assert User.objects.filter(pk=user_1["user"].pk).exists()
    assert response.status_code == 405


@pytest.mark.django_db
def test_anonymous_user_destroy_method(client, user_1):
    url = reverse("users-detail", kwargs={"pk": user_1["user"].pk})
    response = client.delete(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_casual_user_list_method(client, user_1):
    url = reverse('users-list')

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {user_1['token']}"
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_list_method(client, admin_user):
    url = reverse('users-list')

    client.defaults['HTTP_AUTHORIZATION'] = f"Bearer {admin_user['token']}"
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_anonymous_user_list_method(client, user_1):
    url = reverse('users-list')
    response = client.get(url)
    assert response.status_code == 403

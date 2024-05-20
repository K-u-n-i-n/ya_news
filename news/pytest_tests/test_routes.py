from http import HTTPStatus
import pytest
from django.urls import reverse


@pytest.mark.parametrize("name,args", [
    ('news:home', None),
    ('news:detail', pytest.lazy_fixture('news')),
    ('users:login', None),
    ('users:logout', None),
    ('users:signup', None),
])
@pytest.mark.django_db
def test_pages_availability(client, name, args):
    if args is not None:
        url = reverse(name, args=(args.id,))
    else:
        url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("user,status", [
    (pytest.lazy_fixture('author'), HTTPStatus.OK),
    (pytest.lazy_fixture('reader'), HTTPStatus.NOT_FOUND),
])
@pytest.mark.parametrize("name", ['news:edit', 'news:delete'])
@pytest.mark.django_db
def test_availability_for_comment_edit_and_delete(client, user, status, name, comment):
    client.force_login(user)
    url = reverse(name, args=(comment.id,))
    response = client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize("name", ['news:edit', 'news:delete'])
@pytest.mark.django_db
def test_redirect_for_anonymous_client(client, name, comment):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url

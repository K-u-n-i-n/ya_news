from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db

OK = HTTPStatus.OK


@pytest.mark.parametrize("reverse_url,parametrized_client,status", [
    (lf('edit_url'), lf('client_with_login'), OK),
    (lf('edit_url'), lf('client_with_reader_login'), HTTPStatus.NOT_FOUND),
    (lf('delete_url'), lf('client_with_login'), OK),
    (lf('delete_url'), lf('client_with_reader_login'), HTTPStatus.NOT_FOUND),
    (lf('home_url'), lf('client'), OK),
    (lf('login_url'), lf('client'), OK),
    (lf('logout_url'), lf('client'), OK),
    (lf('signup_url'), lf('client'), OK),
])
def test_availability_for_comment_edit_and_delete(
    reverse_url, parametrized_client, status
):
    response = parametrized_client.get(reverse_url)
    assert response.status_code == status


@pytest.mark.parametrize("reverse_url", [
    lf('edit_url'),
    lf('delete_url'),
])
def test_redirect_for_anonymous_client(client, reverse_url):
    """
    Проверяет перенаправление анонимного пользователя на страницу входа
    при попытке редактирования или удаления комментария.

    Параметры:
    - client: клиент без авторизации.
    - reverse_url: URL для редактирования или удаления комментария.

    Ассерты:
    - Статус ответа равен HTTPStatus.FOUND.
    - URL перенаправления соответствует ожидаемому.
    """
    login_url = reverse('users:login')
    redirect_url = f'{login_url}?next={reverse_url}'
    response = client.get(reverse_url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url

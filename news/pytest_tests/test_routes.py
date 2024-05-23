from http import HTTPStatus

import pytest

from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("name,args", [
    ('news:home', None),
    ('news:detail', pytest.lazy_fixture('news')),
    ('users:login', None),
    ('users:logout', None),
    ('users:signup', None),
])
def test_pages_availability(client, name, args):
    """
    Проверяет доступность страниц для анонимного пользователя.

    Параметры:
    - client: клиент без авторизации.
    - name: имя URL паттерна.
    - args: аргументы для реверса URL.

    Ассерты:
    - Статус ответа равен HTTPStatus.OK.
    """
    if args is not None:
        url = reverse(name, args=(args.id,))
    else:
        url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("reverse_url,parametrized_client,status", [
    (pytest.lazy_fixture('delete_url'), pytest.lazy_fixture(
        'client_with_login'), HTTPStatus.OK),
    (pytest.lazy_fixture('delete_url'), pytest.lazy_fixture(
        'client_with_reader_login'), HTTPStatus.NOT_FOUND),
    (pytest.lazy_fixture('edit_url'), pytest.lazy_fixture(
        'client_with_login'), HTTPStatus.OK),
    (pytest.lazy_fixture('edit_url'), pytest.lazy_fixture(
        'client_with_reader_login'), HTTPStatus.NOT_FOUND),
])
def test_availability_for_comment_edit_and_delete(
    reverse_url, parametrized_client, status
):
    """
    Проверяет доступность страниц редактирования и удаления комментария
    для авторизованных пользователей.

    Параметры:
    - reverse_url: URL для редактирования или удаления комментария.
    - parametrized_client: клиент с авторизованным пользователем.
    - status: ожидаемый статус ответа.

    Ассерты:
    - Статус ответа равен ожидаемому статусу.
    """
    # Аутентифицируем клиент перед запросом к серверу
    parametrized_client.force_login(parametrized_client.user)
    response = parametrized_client.get(reverse_url)
    assert response.status_code == status


@pytest.mark.parametrize("reverse_url", [
    pytest.lazy_fixture('edit_url'),
    pytest.lazy_fixture('delete_url'),
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

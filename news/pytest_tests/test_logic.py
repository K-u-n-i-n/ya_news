from http import HTTPStatus

import pytest

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_author_can_delete_comment(client_with_login, delete_url):
    """
    Проверяет, что автор комментария может удалить свой комментарий.

    Параметры:
    - client_with_login: клиент с авторизованным пользователем.
    - delete_url: URL для удаления комментария.

    Ассерты:
    - Статус ответа равен HTTPStatus.FOUND.
    - Количество комментариев уменьшилось на 1.
    """
    initial_comment_count = Comment.objects.count()
    response = client_with_login.delete(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == initial_comment_count - 1


def test_user_cant_delete_comment_of_another_user(
    client_with_reader_login, delete_url
):
    """
    Проверяет, что пользователь не может удалить комментарий
    другого пользователя.

    Параметры:
    - client_with_reader_login: клиент с авторизованным пользователем
    (не автором).
    - delete_url: URL для удаления комментария.

    Ассерты:
    - Статус ответа равен HTTPStatus.NOT_FOUND.
    - Количество комментариев не изменилось.
    """
    initial_comment_count = Comment.objects.count()
    response = client_with_reader_login.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_comment_count


def test_author_can_edit_comment(client_with_login, edit_url, comment):
    """
    Проверяет, что автор комментария может отредактировать свой комментарий.

    Параметры:
    - client_with_login: клиент с авторизованным пользователем.
    - edit_url: URL для редактирования комментария.
    - comment: объект комментария.

    Ассерты:
    - Статус ответа равен HTTPStatus.FOUND.
    - Текст комментария обновлен.
    - Автор и новость комментария остались прежними.
    """
    new_text = 'Обновленный текст комментария'
    response = client_with_login.post(edit_url, {'text': new_text})
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == new_text
    assert comment.author == comment.author
    assert comment.news == comment.news


def test_user_cant_edit_comment_of_another_user(
    client_with_reader_login, edit_url, comment
):
    """
    Проверяет, что пользователь не может отредактировать комментарий
    другого пользователя.

    Параметры:
    - client_with_reader_login: клиент с авторизованным пользователем
    (не автором).
    - edit_url: URL для редактирования комментария.
    - comment: объект комментария.

    Ассерты:
    - Статус ответа равен HTTPStatus.NOT_FOUND.
    - Текст комментария не изменился.
    - Автор и новость комментария остались прежними.
    """
    new_text = 'Обновленный текст комментария'
    response = client_with_reader_login.post(edit_url, {'text': new_text})
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == comment.text
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_anonymous_user_cant_post_comment(client, detail_url):
    """
    Проверяет, что анонимный пользователь не может оставить комментарий.

    Параметры:
    - client: клиент без авторизации.
    - detail_url: URL детальной страницы новости.

    Ассерты:
    - Статус ответа равен HTTPStatus.FOUND.
    - Количество комментариев равно 0.
    """
    response = client.post(
        detail_url,
        data={'text': 'Анонимный комментарий'}
    )
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_authorized_user_can_post_comment(
    client_with_login, detail_url, news, author
):
    """
    Проверяет, что авторизованный пользователь может оставить комментарий.

    Параметры:
    - client_with_login: клиент с авторизованным пользователем.
    - detail_url: URL детальной страницы новости.
    - news: объект новости.
    - author: объект автора комментария.

    Ассерты:
    - Статус ответа равен HTTPStatus.FOUND.
    - Количество комментариев равно 1.
    - Текст комментария соответствует отправленному.
    - Автор и новость комментария соответствуют ожиданиям.
    """
    response = client_with_login.post(
        detail_url,
        data={'text': 'Новый комментарий'}
    )
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    comment = Comment.objects.first()
    assert comment.text == 'Новый комментарий'
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(client_with_login, news):
    """
    Проверяет, что пользователь не может использовать запрещенные слова
    в комментарии.

    Параметры:
    - client_with_login: клиент с авторизованным пользователем.
    - news: объект новости.

    Ассерты:
    - В ответе присутствует форма с ошибкой в поле 'text'.
    - Сообщение об ошибке содержит предупреждение о запрещенных словах.
    - Количество комментариев равно 0.
    """
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = client_with_login.post(url, data=bad_words_data)
    assert 'form' in response.context
    assert 'text' in response.context['form'].errors
    assert WARNING in response.context['form'].errors['text']
    comments_count = Comment.objects.count()
    assert comments_count == 0

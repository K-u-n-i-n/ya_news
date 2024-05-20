import pytest
from http import HTTPStatus
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_author_can_delete_comment(client_with_login, delete_url):
    """Проверяет, что автор комментария может удалить свой комментарий."""
    response = client_with_login.delete(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(client, reader, delete_url):
    """
    Проверяет, что пользователь не может удалить
    комментарий другого пользователя.
    """
    client.force_login(reader)
    response = client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(client_with_login, edit_url, comment):
    """
    Проверяет, что автор комментария может
    отредактировать свой комментарий.
    """
    new_text = 'Обновленный текст комментария'
    response = client_with_login.post(edit_url, {'text': new_text})
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == new_text


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    client, reader, edit_url, comment
):
    """Проверяет, что пользователь не может отредактировать
    комментарий другого пользователя.
    """
    client.force_login(reader)
    new_text = 'Обновленный текст комментария'
    response = client.post(edit_url, {'text': new_text})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'


@pytest.mark.django_db
def test_anonymous_user_cant_post_comment(client, news):
    """Проверяет, что анонимный пользователь не может оставить комментарий."""
    response = client.post(
        reverse('news:detail', args=[news.pk]),
        data={'text': 'Анонимный комментарий'}
    )
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_authorized_user_can_post_comment(client_with_login, news):
    """
    Проверяет, что авторизованный пользователь
    может оставить комментарий.
    """
    response = client_with_login.post(
        reverse('news:detail', args=[news.pk]),
        data={'text': 'Новый комментарий'}
    )
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_user_cant_use_bad_words(client_with_login, news):
    """
    Проверяет, что пользователь не может использовать
    запрещенные слова в комментарии.
    """
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = client_with_login.post(url, data=bad_words_data)
    assert 'form' in response.context
    assert 'text' in response.context['form'].errors
    assert WARNING in response.context['form'].errors['text']
    comments_count = Comment.objects.count()
    assert comments_count == 0

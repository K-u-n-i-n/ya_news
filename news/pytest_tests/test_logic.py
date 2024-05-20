from http import HTTPStatus
from django.urls import reverse
import pytest

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_author_can_delete_comment(client_with_login, delete_url, comment):
    response = client_with_login.delete(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(client, reader, delete_url, comment):
    client.force_login(reader)
    response = client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(client_with_login, edit_url, comment):
    new_text = 'Обновленный текст комментария'
    response = client_with_login.post(edit_url, {'text': new_text})
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == new_text


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(client, reader, edit_url, comment):
    client.force_login(reader)
    new_text = 'Обновленный текст комментария'
    response = client.post(edit_url, {'text': new_text})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'


@pytest.mark.django_db
def test_anonymous_user_cant_post_comment(client, news):
    response = client.post(reverse('news:detail', args=[news.pk]), data={
                           'text': 'Анонимный комментарий'})
    # Ожидаем редирект на страницу логина
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0  # Комментарий не должен быть добавлен


@pytest.mark.django_db
def test_authorized_user_can_post_comment(client_with_login, news):
    response = client_with_login.post(reverse('news:detail', args=[news.pk]), data={
                                      'text': 'Новый комментарий'})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1  # Новый комментарий должен быть добавлен


@pytest.mark.django_db
def test_user_cant_use_bad_words(client_with_login, news):
    # Формируем URL для детального просмотра новости.
    url = reverse('news:detail', args=(news.id,))
    # Формируем данные для отправки формы; текст включает первое слово из списка стоп-слов.
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    # Отправляем запрос через авторизованный клиент.
    response = client_with_login.post(url, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assert 'form' in response.context
    assert 'text' in response.context['form'].errors
    assert WARNING in response.context['form'].errors['text']
    # Дополнительно убедимся, что комментарий не был создан.
    comments_count = Comment.objects.count()
    assert comments_count == 0

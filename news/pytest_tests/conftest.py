import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import datetime

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def news():
    """Создает и возвращает объект News."""
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def author(db):
    """Создает и возвращает объект User с именем 'Лев Толстой'."""
    return User.objects.create(username='Лев Толстой')


@pytest.fixture
def reader(db):
    """Создает и возвращает объект User с именем 'Читатель простой'."""
    return User.objects.create(username='Читатель простой')


@pytest.fixture
def comment(news, author):
    """Создает и возвращает объект Comment, связанный с новостью и автором."""
    return Comment.objects.create(
        news=news, author=author, text='Текст комментария'
    )


@pytest.fixture
def client_with_login(client, author):
    """Авторизует клиента с помощью созданного пользователя (автора)."""
    client.force_login(author)
    return client


@pytest.fixture
def detail_url(news):
    """Возвращает URL для детального просмотра новости."""
    return reverse('news:detail', args=[news.id])


@pytest.fixture
def comments(news, author):
    """
    Создает и возвращает список из 5 комментариев к новости от одного автора.
    """
    comments = []
    for i in range(5):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}',
            created=datetime(2023, 1, 1, 12, 0, i)
        )
        comments.append(comment)
    return comments


@pytest.fixture
def edit_url(comment):
    """Возвращает URL для редактирования комментария."""
    return reverse('news:edit', args=[comment.pk])


@pytest.fixture
def delete_url(comment):
    """Возвращает URL для удаления комментария."""
    return reverse('news:delete', args=[comment.pk])

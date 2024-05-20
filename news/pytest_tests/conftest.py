import pytest
from django.contrib.auth import get_user_model
from news.models import Comment, News
from django.urls import reverse
from datetime import datetime

User = get_user_model()


@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def author(db):
    return User.objects.create(username='Лев Толстой')


@pytest.fixture
def reader(db):
    return User.objects.create(username='Читатель простой')


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(news=news, author=author, text='Текст комментария')


@pytest.fixture
def client_with_login(client, author):
    client.force_login(author)
    return client


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=[news.id])


@pytest.fixture
def comments(news, author):
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
    return reverse('news:edit', args=[comment.pk])


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=[comment.pk])

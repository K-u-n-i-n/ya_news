from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def home_url():
    """Возвращает URL главной страницы."""
    return reverse('news:home')


@pytest.fixture
def login_url():
    """Возвращает URL страницы входа."""
    return reverse('users:login')


@pytest.fixture
def logout_url():
    """Возвращает URL страницы выхода."""
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    """Возвращает URL страницы регистрации."""
    return reverse('users:signup')


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
def client_with_login(author):
    """Авторизует клиента с помощью созданного пользователя (автора)."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def client_with_reader_login(reader):
    """Авторизует клиента с помощью созданного пользователя (читателя)."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def detail_url(news):
    """Возвращает URL для детального просмотра новости."""
    return reverse('news:detail', args=[news.id])


@pytest.fixture
def news_list():
    """Создает новости для тестирования."""
    news_count = settings.NEWS_COUNT_ON_HOME_PAGE + 1
    news_items = [
        News(title=f'Заголовок {i}',
             text='Текст',
             date=datetime.now() - timedelta(days=i)
             )
        for i in range(news_count)
    ]
    News.objects.bulk_create(news_items)


@pytest.fixture
def comments(news, author):
    """Создает 5 комментариев к новости от одного автора."""
    for i in range(5):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}'
        )
        comment.created = datetime.today() - timedelta(days=i)
        comment.save()


@pytest.fixture
def edit_url(comment):
    """Возвращает URL для редактирования комментария."""
    return reverse('news:edit', args=[comment.pk])


@pytest.fixture
def delete_url(comment):
    """Возвращает URL для удаления комментария."""
    return reverse('news:delete', args=[comment.pk])

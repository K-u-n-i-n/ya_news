import pytest
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
class TestNews:
    """Тесты для приложения новостей."""

    def test_comments_order(self, client, detail_url):
        """
        Проверяет, что комментарии к новости отображаются в хронологическом
        порядке.

        Параметры:
            client (Client): Тестовый клиент Django.
            detail_url (str): URL для детального просмотра новости.
            comments (list): Список комментариев к новости.

        Ассерты:
            - Комментарии должны быть отсортированы по времени создания
            в порядке возрастания.
        """
        response = client.get(detail_url)
        news = response.context['news']
        all_comments = news.comment_set.all()
        all_timestamps = [comment.created for comment in all_comments]
        sorted_timestamps = sorted(all_timestamps)
        assert all_timestamps == sorted_timestamps

    def test_anonymous_client_has_no_form(self, client, detail_url):
        """
        Проверяет, что анонимный пользователь не видит форму для добавления
        комментария.

        Параметры:
            client (Client): Тестовый клиент Django.
            detail_url (str): URL для детального просмотра новости.

        Ассерты:
            - Форма для добавления комментария не должна присутствовать
            в контексте ответа.
        """
        response = client.get(detail_url)
        assert 'form' not in response.context

    def test_authorized_client_has_form(self, client_with_login, detail_url):
        """
        Проверяет, что авторизованный пользователь видит форму для добавления
        комментария.

        Параметры:
            client_with_login (Client): Авторизованный тестовый клиент Django.
            detail_url (str): URL для детального просмотра новости.

        Ассерты:
            - Форма для добавления комментария должна присутствовать
            в контексте ответа.
            - Форма должна быть экземпляром класса CommentForm.
        """
        response = client_with_login.get(detail_url)
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)

    def test_news_count_on_homepage(self, client, news_list, home_url):
        """
        Проверяет, что на главной странице отображается ровно столько новостей,
        сколько задано в NEWS_COUNT_ON_HOME_PAGE.

        Параметры:
            client (Client): Тестовый клиент Django.
            news_list: новости для тестирования.
            home_url: URL главной страницы.

        Ассерты:
            - На главной странице должно отображаться не более 10 новостей.
        """
        response = client.get(home_url)
        assert response.context[
            'news_list'
        ].count() == settings.NEWS_COUNT_ON_HOME_PAGE

    def test_news_order_on_homepage(self, client, news_list, home_url):
        """
        Проверяет, что новости на главной странице отображаются в порядке
        убывания даты.

        Параметры:
            client (Client): Тестовый клиент Django.
            news_list: новости для тестирования.
            home_url: URL главной страницы.

        Ассерты:
            - Новости на главной странице должны быть отсортированы по дате
            в порядке убывания.
        """
        response = client.get(home_url)
        news_list = response.context['news_list']
        timestamps = [news.date for news in news_list]
        sorted_timestamps = sorted(timestamps, reverse=True)
        assert timestamps == sorted_timestamps

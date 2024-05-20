import pytest
from http import HTTPStatus
from django.urls import reverse

from news.forms import CommentForm
from news.models import News


@pytest.mark.django_db
class TestNews:

    def test_comments_order(self, client, detail_url, comments):
        response = client.get(detail_url)
        assert 'news' in response.context
        news = response.context['news']
        all_comments = news.comment_set.all()
        all_timestamps = [comment.created for comment in all_comments]
        sorted_timestamps = sorted(all_timestamps)
        assert all_timestamps == sorted_timestamps

    def test_anonymous_client_has_no_form(self, client, detail_url):
        response = client.get(detail_url)
        assert 'form' not in response.context

    def test_authorized_client_has_form(self, client_with_login, detail_url):
        response = client_with_login.get(detail_url)
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)

    def test_news_count_on_homepage(self, client):
        for i in range(15):
            News.objects.create(title=f'Заголовок {i}', text='Текст')
        response = client.get(reverse('news:home'))
        assert len(response.context['news_list']) == 10

    def test_news_order_on_homepage(self, client):
        for i in range(5):
            News.objects.create(title=f'Заголовок {i}', text='Текст')
        response = client.get(reverse('news:home'))
        news_list = response.context['news_list']
        timestamps = [news.date for news in news_list]
        sorted_timestamps = sorted(timestamps, reverse=True)
        assert timestamps == sorted_timestamps

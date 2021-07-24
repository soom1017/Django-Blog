from typing import Text
from django.http import response
from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_ria = User.objects.create_user(username='Ria', password='password')
        self.user_hyo = User.objects.create_user(username='Hyo', password='password')

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

        self.tag_hack = Tag.objects.create(name='해킹 공부', slug='해킹-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_develop = Tag.objects.create(name='develop', slug='develop')

        self.post_001 = Post.objects.create(
            title = '첫번째 포스트입니다',
            content = '첫번째 포스트 테스트 중',
            category = self.category_programming,
            author = self.user_ria,
        )
        self.post_001.tags.add(self.tag_develop)

        self.post_002 = Post.objects.create(
            title ='두번째 포스트입니다',
            content = '두번째 포스트 테스트 중',
            category = self.category_music,
            author = self.user_hyo,
        )
        self.post_002.tags.add(self.tag_hack)
        self.post_002.tags.add(self.tag_python)

        self.post_003 = Post.objects.create(
            title='세번째 포스트입니다',
            content = 'category가 없는 포스트',
            author = self.user_ria,
        )

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_music.name} ({self.category_music.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)

        logo_btn = navbar.find('a', text='Do it Django')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def test_post_list(self):
        #포스트가 있는 경우
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.user_ria.username.upper(), post_001_card.text)
        self.assertIn(self.tag_develop.name, post_001_card.text)
        self.assertNotIn(self.tag_hack.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)


        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertIn(self.user_hyo.username.upper(), post_002_card.text)
        self.assertNotIn(self.tag_develop.name, post_002_card.text)
        self.assertIn(self.tag_hack.name, post_002_card.text)
        self.assertIn(self.tag_python.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn('미분류', post_003_card.text)
        self.assertNotIn(self.tag_develop.name, post_003_card.text)
        self.assertNotIn(self.tag_hack.name, post_003_card.text)
        self.assertNotIn(self.tag_python.name, post_003_card.text)

        #포스트가 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')

        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    def test_post_detail(self):
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.post_001.title, soup.title.text)

        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)

        self.assertIn(self.user_ria.username.upper(), post_area.text)
        self.assertIn(self.post_001.content, post_area.text)
        self.assertIn(self.tag_develop.name, post_area.text)
        self.assertNotIn(self.tag_hack.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)

    def test_category_page(self):
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_programming.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)
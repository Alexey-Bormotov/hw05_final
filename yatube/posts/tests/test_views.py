import shutil
import tempfile
from time import sleep

from django.core.cache import cache
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from ..models import Comment, Following, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
TEST_POST_TEXT = 'Тестовый пост №13 тестового пользователя в тестовой группе'
TEST_COMMENT_TEXT = 'Тестовый комментарий к посту'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user_2 = User.objects.create_user(
            username='test_user_2'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание 2',
        )
        Following.objects.create(
            user=cls.user,
            author=cls.user_2,
        )
        Following.objects.create(
            user=cls.user_2,
            author=cls.user,
        )

        cls.post_2 = Post.objects.create(
            author=cls.user_2,
            group=cls.group,
            text='Тестовый пост для проверки подписки',
        )

        for i in range(12):
            Post.objects.create(
                author=cls.user,
                group=cls.group2,
                text=f'Тестовый пост №{i+1} тестового '
                     f'пользователя в тестовой группе 2',
            )
            sleep(0.01)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text=TEST_POST_TEXT,
            image=uploaded,
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text=TEST_COMMENT_TEXT,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.auth_client = Client()
        self.auth_client_2 = Client()

        self.auth_client.force_login(PostsViewsTests.user)
        self.auth_client_2.force_login(PostsViewsTests.user_2)

    def test_posts_urls_uses_correct_templates(self):
        """URL-адреса используют соответствующие шаблоны в приложении Posts."""
        group = PostsViewsTests.group
        user = PostsViewsTests.user
        post = PostsViewsTests.post

        urls_templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts',
                kwargs={'slug': group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post.pk}
            ): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }

        for url, template in urls_templates_names.items():
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_404_error_uses_correct_custom_template(self):
        """Страница с ошибкой 404 отдаёт кастомный шаблон."""
        response = self.auth_client.get('/fake_page/')

        self.assertTemplateUsed(response, 'core/404.html')

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.auth_client.get(reverse('posts:index'))

        context_post = response.context['page_obj'][0]
        post_author = context_post.author.username
        post_group = context_post.group.title
        post_text = context_post.text
        post_image = context_post.image

        self.assertEqual(post_author, 'test_user')
        self.assertEqual(post_group, 'Тестовая группа')
        self.assertEqual(
            post_text,
            TEST_POST_TEXT
        )
        self.assertEqual(post_image, 'posts/small.gif')

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        group = PostsViewsTests.group
        response = self.auth_client.get(
            reverse('posts:group_posts', kwargs={'slug': group.slug})
        )

        context_post = response.context['page_obj'][0]
        post_author = context_post.author.username
        post_group = context_post.group.title
        post_text = context_post.text
        post_image = context_post.image
        context_group = response.context['group'].title

        self.assertEqual(post_author, 'test_user')
        self.assertEqual(post_group, 'Тестовая группа')
        self.assertEqual(context_group, 'Тестовая группа')
        self.assertEqual(
            post_text,
            TEST_POST_TEXT
        )
        self.assertEqual(post_image, 'posts/small.gif')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        user = PostsViewsTests.user
        posts_count = user.posts.count()
        response = self.auth_client.get(
            reverse('posts:profile', kwargs={'username': user.username})
        )

        context_post = response.context['page_obj'][0]
        post_author = context_post.author.username
        post_group = context_post.group.title
        post_text = context_post.text
        post_image = context_post.image
        context_author = response.context['author'].username
        context_posts_count = response.context['posts_count']

        self.assertEqual(post_author, 'test_user')
        self.assertEqual(context_author, 'test_user')
        self.assertEqual(post_group, 'Тестовая группа')
        self.assertEqual(
            post_text,
            TEST_POST_TEXT
        )
        self.assertEqual(context_posts_count, posts_count)
        self.assertEqual(post_image, 'posts/small.gif')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        user = PostsViewsTests.user
        posts_count = user.posts.count()
        post = PostsViewsTests.post
        response = self.auth_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post.pk})
        )

        context_post = response.context['post']
        post_author = context_post.author.username
        post_group = context_post.group.title
        post_text = context_post.text
        post_image = context_post.image
        context_posts_count = response.context['posts_count']

        self.assertEqual(post_author, 'test_user')
        self.assertEqual(post_group, 'Тестовая группа')
        self.assertEqual(
            post_text,
            TEST_POST_TEXT
        )
        self.assertEqual(context_posts_count, posts_count)
        self.assertEqual(post_image, 'posts/small.gif')

    def test_post_create_show_correct_context(self):
        """Шаблон create_post (create) сформирован с правильным контекстом."""
        response = self.auth_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон create_post (edit) сформирован с правильным контекстом."""
        post = PostsViewsTests.post
        response = self.auth_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post.pk})
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        context_post_id = response.context['post_id']

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(context_post_id, 14)

    def test_posts_pages_correct_paginator_work(self):
        """Проверка работы паджинатора в шаблонах приложения Posts."""
        group = PostsViewsTests.group2
        user = PostsViewsTests.user
        PAGE_1_POSTS = 10

        urls_page2posts_names = {
            reverse('posts:index'): 4,
            reverse('posts:group_posts', kwargs={'slug': group.slug}): 2,
            reverse('posts:profile', kwargs={'username': user.username}): 3,
        }

        for page, page_2_posts in urls_page2posts_names.items():
            with self.subTest(page=page):
                response_page_1 = self.auth_client.get(page)
                response_page_2 = self.auth_client.get(page + '?page=2')

                self.assertEqual(
                    len(response_page_1.context['page_obj']),
                    PAGE_1_POSTS
                )
                self.assertEqual(
                    len(response_page_2.context['page_obj']),
                    page_2_posts
                )

    def test_post_correct_appear(self):
        ("""Проверка, что созданный пост появляется на """
         """нужных страницах.""")
        group = PostsViewsTests.group
        user = PostsViewsTests.user
        post = PostsViewsTests.post

        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': group.slug}),
            reverse('posts:profile', kwargs={'username': user.username}),
        ]

        for page in pages_names:
            with self.subTest(page=page):
                response = self.auth_client.get(page)
                context_post = response.context['page_obj'][0]

                self.assertEqual(context_post, post)

    def test_post_correct_not_appear(self):
        ("""Проверка, что созданный пост не появляется в группе """
         """к которой он не принадлежит.""")
        group2 = PostsViewsTests.group2
        post = PostsViewsTests.post
        page = reverse('posts:group_posts', kwargs={'slug': group2.slug})

        response = self.auth_client.get(page)
        context_post = response.context['page_obj'][0]

        self.assertNotEqual(context_post, post)

    def test_comment_correct_appear(self):
        ("""Проверка, что созданный комментарий появляется на """
         """странице с постом.""")
        post = PostsViewsTests.post
        comment = PostsViewsTests.comment

        response = self.auth_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post.pk})
        )

        context_comment = response.context['comments'][0]

        self.assertEqual(context_comment, comment)

    def test_index_page_caching(self):
        """Проверка кеширования шаблона index."""
        post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='Пост для удаления',
        )

        response1 = self.auth_client.get(reverse('posts:index'))
        post.delete()
        response2 = self.auth_client.get(reverse('posts:index'))
        cache.clear()
        response3 = self.auth_client.get(reverse('posts:index'))

        self.assertEqual(response1.content, response2.content)
        self.assertNotEqual(response2.content, response3.content)

    def test_post_correct_appear_at_follow_template(self):
        ("""Проверка, что созданный пост появляется на странице избранных"""
         """авторов у подписчиков и не появляется у тех, кто не подписан.""")
        post = PostsViewsTests.post
        not_follower_response = self.auth_client.get(
            reverse('posts:follow_index')
        )
        follower_response = self.auth_client_2.get(
            reverse('posts:follow_index')
        )

        not_follower_post = not_follower_response.context['page_obj'][0]
        follower_post = follower_response.context['page_obj'][0]

        self.assertNotEqual(post, not_follower_post)
        self.assertEqual(post, follower_post)

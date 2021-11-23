from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user_not_author = User.objects.create_user(
            username='test_user_not_author'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост тестового пользователя в тестовой группе',
        )

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client_not_author = Client()

        self.auth_client.force_login(PostsURLTests.user)
        self.auth_client_not_author.force_login(PostsURLTests.user_not_author)

    def test_urls_exists_at_desired_location(self):
        """Проверяем доступность страниц приложения Posts."""
        group = PostsURLTests.group
        user = PostsURLTests.user
        post = PostsURLTests.post

        url_names = [
            '/',
            f'/group/{group.slug}/',
            f'/profile/{user.username}/',
            f'/posts/{post.pk}/',
        ]

        for address in url_names:
            with self.subTest(address=address):
                guest_response = self.guest_client.get(address, follow=True)
                auth_response = self.auth_client.get(address)

                self.assertEqual(guest_response.reason_phrase, 'OK')
                self.assertEqual(auth_response.reason_phrase, 'OK')

    def test_post_edit_url_exists_at_desired_location(self):
        ("""Проверяем доступность страницы редактирования поста """
         """приложения Posts.""")
        post = PostsURLTests.post
        address = f'/posts/{post.pk}/edit/'

        guest_response = self.guest_client.get(address, follow=True)
        auth_response = self.auth_client.get(address)
        auth_not_author_response = (
            self.auth_client_not_author.get(address)
        )

        self.assertRedirects(
            guest_response,
            f'/auth/login/?next=/posts/{post.pk}/edit/'
        )
        self.assertEqual(auth_response.reason_phrase, 'OK')
        self.assertEqual(
            auth_not_author_response.url,
            f'/posts/{post.pk}'
        )

    def test_create_post_url_exists_at_desired_location(self):
        ("""Проверяем доступность страницы создания поста """
         """приложения Posts.""")
        address = f'{"/create/"}'

        guest_response = self.guest_client.get(address, follow=True)
        auth_response = self.auth_client.get(address)

        self.assertRedirects(
            guest_response,
            f'{"/auth/login/?next=/create/"}'
        )
        self.assertEqual(auth_response.reason_phrase, 'OK')

    def test_post_comment_url_exists_at_desired_location(self):
        ("""Проверяем возможность комментирования поста """
         """приложения Posts.""")
        post = PostsURLTests.post
        address = f'/posts/{post.pk}/comment/'

        guest_response = self.guest_client.get(address, follow=True)
        auth_response = self.auth_client.get(address)

        self.assertRedirects(
            guest_response,
            f'/auth/login/?next=/posts/{post.pk}/comment/'
        )
        self.assertEqual(auth_response.reason_phrase, 'Found')

    def test_following_url_exists_at_desired_location(self):
        ("""Проверяем доступность подписки и отписки в """
         """приложении Posts.""")
        user = PostsURLTests.user

        url_names = [
            f'/profile/{user.username}/follow/',
            f'/profile/{user.username}/unfollow/',
        ]

        for address in url_names:
            with self.subTest(address=address):
                guest_response = self.guest_client.get(address, follow=True)
                auth_response = self.auth_client_not_author.get(address)

                self.assertRedirects(
                    guest_response,
                    f'/auth/login/?next={address}'
                )
                self.assertEqual(auth_response.reason_phrase, 'Found')

    def test_404_error_return_for_unexisting_page(self):
        ("""Проверяем возврат ошибки 404 при запросе к """
         """несуществующей странице.""")
        address = f'{"/fake_page/"}'

        guest_response = self.guest_client.get(address, follow=True)
        auth_response = self.auth_client.get(address)

        self.assertEqual(guest_response.reason_phrase, 'Not Found')
        self.assertEqual(auth_response.reason_phrase, 'Not Found')

    def test_urls_uses_correct_template(self):
        """Проверяем шаблоны приложения Posts."""
        group = PostsURLTests.group
        user = PostsURLTests.user
        post = PostsURLTests.post

        url_templates_names = {
            '/': 'posts/index.html',
            f'/group/{group.slug}/': 'posts/group_list.html',
            f'/profile/{user.username}/': 'posts/profile.html',
            f'/posts/{post.pk}/': 'posts/post_detail.html',
            f'/posts/{post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }

        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.auth_client.get(address)
                self.assertTemplateUsed(response, template)

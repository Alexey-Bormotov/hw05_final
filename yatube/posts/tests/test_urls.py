from . import posts_tests_setup as setup


class PostsURLTests(setup.PostsTestsSetup):
    def test_urls_exists_at_desired_location(self):
        """Проверяем доступность страниц приложения Posts."""

        url_names = [
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.pk}/',
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

        address = f'/posts/{self.post.pk}/edit/'

        guest_response = self.guest_client.get(address, follow=True)
        auth_response = self.auth_client.get(address)
        auth_not_author_response = (
            self.auth_client_not_author.get(address)
        )

        self.assertRedirects(
            guest_response,
            f'/auth/login/?next={address}'
        )
        self.assertEqual(auth_response.reason_phrase, 'OK')
        self.assertEqual(
            auth_not_author_response.url,
            f'/posts/{self.post.pk}'
        )

    def test_create_post_url_exists_at_desired_location(self):
        ("""Проверяем доступность страницы создания поста """
         """приложения Posts.""")

        address = f'{"/create/"}'

        guest_response = self.guest_client.get(address, follow=True)
        auth_response = self.auth_client.get(address)

        self.assertRedirects(
            guest_response,
            f'/auth/login/?next={address}'
        )
        self.assertEqual(auth_response.reason_phrase, 'OK')

    def test_post_comment_url_exists_at_desired_location(self):
        ("""Проверяем возможность комментирования поста """
         """приложения Posts.""")

        address = f'/posts/{self.post.pk}/comment/'

        guest_response = self.guest_client.get(address, follow=True)
        auth_response = self.auth_client.get(address)

        self.assertRedirects(
            guest_response,
            f'/auth/login/?next={address}'
        )
        self.assertEqual(auth_response.reason_phrase, 'Found')

    def test_following_urls_for_guest(self):
        ("""Проверяем недоступность подписки и отписки в """
         """приложении Posts для гостя.""")

        url_names = [
            f'/profile/{self.user.username}/follow/',
            f'/profile/{self.user.username}/unfollow/',
        ]

        for address in url_names:
            with self.subTest(address=address):
                guest_response = self.guest_client.get(address, follow=True)

                self.assertRedirects(
                    guest_response,
                    f'/auth/login/?next={address}'
                )

    def test_following_urls_for_auth_user(self):
        ("""Проверяем доступность подписки и отписки в """
         """приложении Posts для авторизованного пользователя.""")

        url_names = [
            f'/profile/{self.user.username}/follow/',
            f'/profile/{self.user.username}/unfollow/',
        ]

        for address in url_names:
            with self.subTest(address=address):
                auth_response = self.auth_client_not_author.get(address)

                self.assertEqual(auth_response.status_code, 302)

    def test_404_error_return_for_unexisting_page(self):
        ("""Проверяем возврат ошибки 404 при запросе к """
         """несуществующей странице.""")

        address = f'{"/fake_page/"}'

        users_requests = [
            self.guest_client.get(address),
            self.auth_client.get(address),
        ]

        for request in users_requests:
            with self.subTest(request=request):

                self.assertEqual(request.reason_phrase, 'Not Found')

    def test_urls_uses_correct_template(self):

        url_templates_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }

        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.auth_client.get(address)
                self.assertTemplateUsed(response, template)

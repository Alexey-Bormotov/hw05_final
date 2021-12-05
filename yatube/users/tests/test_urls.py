from . import users_tests_setup as setup


class UsersURLTests(setup.UsersTestsSetup):
    def test_urls_exists_at_desired_location(self):
        """Проверяем доступность страниц приложения Users."""

        url_names = [
            '/auth/login/',
            '/auth/signup/',
            '/auth/password_change/',
            '/auth/password_reset/',
            '/auth/logout/',
        ]

        for address in url_names:
            with self.subTest(address=address):
                guest_response = self.guest_client.get(address, follow=True)
                auth_response = self.auth_client.get(address)

                if address == '/auth/password_change/':
                    self.assertRedirects(
                        guest_response,
                        f'{"/auth/login/?next=/auth/password_change/"}'
                    )
                    self.assertEqual(auth_response.reason_phrase, 'OK')

                self.assertEqual(guest_response.reason_phrase, 'OK')
                self.assertEqual(auth_response.reason_phrase, 'OK')

    def test_urls_uses_correct_template(self):
        """Проверяем шаблоны приложения Users."""

        url_templates_names = {
            '/auth/login/': 'users/login.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/logout/': 'users/logged_out.html',
        }

        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.auth_client.get(address)
                self.assertTemplateUsed(response, template)

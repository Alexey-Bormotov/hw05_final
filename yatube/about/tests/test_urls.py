from . import about_tests_setup as setup


class AboutURLTests(setup.AboutTestsSetup):
    def test_about_urls_exists_at_desired_locations(self):
        """Проверяем доступность страниц по URL приложения About."""

        url_names = [
            '/about/author/',
            '/about/tech/',
        ]

        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.reason_phrase, 'OK')

    def test_about_urls_uses_correct_template(self):
        """Проверяем шаблоны страниц приложения About."""

        url_templates_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

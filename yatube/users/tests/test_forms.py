from django.contrib.auth import get_user_model
from django.urls import reverse

from . import users_tests_setup as setup

User = get_user_model()


class UsersFormsTests(setup.UsersTestsSetup):
    def test_user_create(self):
        """Валидная форма создает запись в User."""

        users_count = User.objects.count()

        form_data = {
            'first_name': 'Юзер',
            'last_name': 'Тестовый',
            'username': 'test_user_2',
            'email': 'test_user@yandex.ru',
            'password1': '12345asD!',
            'password2': '12345asD!',
        }

        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name='Юзер',
                last_name='Тестовый',
                username='test_user_2',
                email='test_user@yandex.ru',
            ).exists()
        )

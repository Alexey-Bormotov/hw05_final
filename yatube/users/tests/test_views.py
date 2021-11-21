from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

User = get_user_model()


class UsersViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')

    def setUp(self):
        self.auth_client = Client()

        self.auth_client.force_login(UsersViewsTests.user)

    def test_users_pages_uses_correct_templates(self):
        """URL-адреса используют соответствующие шаблоны в приложении Users."""

        pages_templates_names = {
            reverse('users:login'): 'users/login.html',
            reverse('users:signup'): 'users/signup.html',
            reverse('users:password_change'): (
                'users/password_change_form.html'
            ),
            reverse('users:password_reset'): 'users/password_reset_form.html',
            reverse('users:logout'): 'users/logged_out.html',
        }

        for reverse_name, template in pages_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_users_pages_show_correct_contexts(self):
        """Проверка правильности контекстов страниц приложения Users."""

        pages_contexts_names = {
            reverse('users:signup'): ('form',),
        }

        for reverse_name, context in pages_contexts_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth_client.get(reverse_name)

                for context_obj in context:
                    if context_obj == 'form':
                        form_fields = {
                            'first_name': forms.fields.CharField,
                            'last_name': forms.fields.CharField,
                            'username': forms.fields.CharField,
                            'email': forms.fields.EmailField,
                        }

                        for value, expected in form_fields.items():
                            with self.subTest(value=value):
                                form_field = (
                                    response.context.get('form').
                                    fields.get(value)
                                )
                                self.assertIsInstance(form_field, expected)

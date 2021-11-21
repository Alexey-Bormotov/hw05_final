from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostsModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
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

    def test_group_object_name(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = PostsModelTests.group

        expected_group_str = group.title

        self.assertEqual(expected_group_str, str(group))

    def test_post_object_name(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostsModelTests.post

        expected_post_str = post.text[:15]

        self.assertEqual(expected_post_str, str(post))

    def test_post_verbose_name(self):
        """Проверяем, verbose_name'ы у модели Post."""
        post = PostsModelTests.post

        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка',
        }

        for field, expected_verbose in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_verbose
                )

    def test_post_help_text(self):
        """Проверяем, help_text'ы у модели Post."""
        post = PostsModelTests.post

        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
            'image': 'Загрузите картинку',
        }

        for field, expected_help_text in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_help_text
                )

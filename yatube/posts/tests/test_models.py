from . import posts_tests_setup as setup


class PostsModelTests(setup.PostsTestsSetup):
    def test_group_object_name(self):
        """Проверяем, что у модели Group корректно работает __str__."""

        expected_group_str = self.group.title

        self.assertEqual(expected_group_str, str(self.group))

    def test_post_object_name(self):
        """Проверяем, что у модели Post корректно работает __str__."""

        expected_post_str = self.post.text[:15]

        self.assertEqual(expected_post_str, str(self.post))

    def test_post_verbose_name(self):
        """Проверяем, verbose_name'ы у модели Post."""

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
                    self.post._meta.get_field(field).verbose_name,
                    expected_verbose
                )

    def test_post_help_text(self):
        """Проверяем, help_text'ы у модели Post."""

        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
            'image': 'Загрузите картинку',
        }

        for field, expected_help_text in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    expected_help_text
                )

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import Comment, Post
from . import posts_tests_setup as setup

User = get_user_model()

TEST_POST_TEXT = 'Тестовый пост'
TEST_POST_TEXT_2 = 'Изменённый тестовый пост'
TEST_COMMENT_TEXT = 'Тестовый комментарий к посту'


class PostsFormsTests(setup.PostsTestsSetup):
    def test_posts_create_post(self):
        """Валидная форма создает запись в Post."""

        posts_count = Post.objects.count()

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

        form_data = {
            'text': TEST_POST_TEXT,
            'group': self.group.pk,
            'image': uploaded,
        }

        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=TEST_POST_TEXT,
                group=self.group,
                author=self.user,
                image='posts/small.gif'
            ).exists()
        )

    def test_posts_edit_post(self):
        """Валидная форма редактирует запись в Post."""

        posts_count = Post.objects.count()

        form_data = {
            'text': TEST_POST_TEXT_2,
            'group': self.group.pk,
        }

        self.auth_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(
            Post.objects.get(pk=self.post.pk).text,
            TEST_POST_TEXT_2
        )

    def test_posts_user_creates_comment(self):
        """Валидная форма создает комментарий в Comment."""

        comments_count = Comment.objects.count()

        form_data = {
            'text': TEST_COMMENT_TEXT,
        }

        response = self.auth_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(text=TEST_COMMENT_TEXT).exists()
        )

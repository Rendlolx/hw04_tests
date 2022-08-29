import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug_test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.user,
        )

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Неавторизованный клиент"""
        self.guest_client = Client()

        """Авторизованный юзер"""
        self.user = User.objects.create_user(username='Sereja')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        """Автор"""
        self.author_client = Client()
        self.author_client.force_login(PostCreateFormTests.post.author)

    def test_create_post(self):
        post_count = Post.objects.count()
        response = self.author_client.post(
            reverse('posts:post_create'),
            data={
                'text': PostCreateFormTests.post.text,
                'group': PostCreateFormTests.group.id
            },
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), post_count + 1)

        post = Post.objects.first()
        self.assertEqual(post.text, PostCreateFormTests.post.text)
        self.assertEqual(post.author, PostCreateFormTests.post.author)
        self.assertEqual(post.group, PostCreateFormTests.group)

        """Валидная форма создает запись в Post."""
        form_data = {
            'text': f'{PostCreateFormTests.post.text}',
            'group': f'{PostCreateFormTests.group.id}',
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostCreateFormTests.post.author}
            )
        )

        self.assertTrue(
            Post.objects.filter(
                text=f'{PostCreateFormTests.post.text}',
                group=f'{PostCreateFormTests.group.id}',
            ).exists()
        )

    def test_post_edit(self):
        post_count = Post.objects.count()
        post = Post.objects.create(
            text=PostCreateFormTests.post.text,
            author=PostCreateFormTests.post.author,
            group=PostCreateFormTests.group
        )
        new_post_text = PostCreateFormTests.post.text
        new_group = Group.objects.create(
            title=PostCreateFormTests.group.title,
            slug='slug_2',
            description=PostCreateFormTests.group.description
        )

        self.author_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{PostCreateFormTests.post.id}'}),
            data={
                'text': new_post_text,
                'group': new_group.id},
            follow=True,
        )

        self.assertEqual(Post.objects.count(), post_count + 1)
        post = Post.objects.first()
        self.assertEqual(post.text, new_post_text)
        self.assertEqual(post.author, PostCreateFormTests.post.author)
        self.assertEqual(post.group.title, new_group.title)

        """Валидная форма редактирует запись"""
        form_data = {
            'group': f'{PostCreateFormTests.group.id}',
            'text': f'{PostCreateFormTests.post.text}',
        }
        response = self.author_client.post(
            reverse("posts:post_edit",
                    kwargs={'post_id': f'{PostCreateFormTests.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail",
                    kwargs={"post_id": f'{PostCreateFormTests.post.id}'})
        )
        self.assertEqual(
            Post.objects.first().text,
            f'{PostCreateFormTests.post.text}'
        )
        self.assertEqual(
            Post.objects.first().group.title,
            f'{PostCreateFormTests.group.title}'
        )

    def test_create_post_non_authorized_client(self):
        post_count = Post.objects.count()
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data={
                'text': PostCreateFormTests.post.text,
                'group': PostCreateFormTests.group.id
            },
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)

        self.assertRedirects(
            response,
            '/auth/login/?next=/create/'
        )

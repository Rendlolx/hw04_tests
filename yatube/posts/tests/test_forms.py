import shutil
import tempfile

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
            author=cls.user
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
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
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

        self.assertEqual(Post.objects.count(), post_count + 1)

        self.assertTrue(
            Post.objects.filter(
                text=f'{PostCreateFormTests.post.text}',
                group=f'{PostCreateFormTests.group.id}'
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма редактирует запись"""

        post_count = Post.objects.count()
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
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(
            Post.objects.first().text,
            f'{PostCreateFormTests.post.text}'
        )
        self.assertEqual(
            Post.objects.first().group.title,
            f'{PostCreateFormTests.group.title}'
        )

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostViewsTest(TestCase):
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
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        """Авторизованный юзер"""
        self.user = User.objects.create_user(username='Sereja')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        """Автор"""
        self.author_client = Client()
        self.author_client.force_login(PostViewsTest.post.author)

    def test_right_template_in_views(self):
        dict_templates = {
            reverse('posts:main'): 'posts/index.html',
            reverse(
                'posts:group', kwargs={'slug': PostViewsTest.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': PostViewsTest.post.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': PostViewsTest.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': PostViewsTest.post.id}
            ): 'posts/create_post.html'
        }
        for reverse_name, template in dict_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_show_correct_context(self):
        response = self.author_client.get(reverse('posts:main'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, f'{PostViewsTest.post.text}')
        self.assertEqual(post_author_0, f'{PostViewsTest.post.author}')
        self.assertEqual(post_group_0, f'{PostViewsTest.group.title}')
        self.assertEqual(post_image_0, f'{PostViewsTest.post.image}')

    def test_page_group_show_correct_context(self):
        response = self.author_client.get(
            reverse('posts:group',
                    kwargs={'slug': PostViewsTest.group.slug})
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, f'{PostViewsTest.post.text}')
        self.assertEqual(post_author_0, f'{PostViewsTest.post.author}')
        self.assertEqual(post_group_0, f'{PostViewsTest.group.title}')
        self.assertEqual(post_image_0, f'{PostViewsTest.post.image}')

    def test_page_profile_show_correct_context(self):
        response = self.author_client.get(
            reverse('posts:profile',
                    kwargs={'username': PostViewsTest.post.author})
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, f'{PostViewsTest.post.text}')
        self.assertEqual(post_author_0, f'{PostViewsTest.post.author}')
        self.assertEqual(post_group_0, f'{PostViewsTest.group.title}')
        self.assertEqual(post_image_0, f'{PostViewsTest.post.image}')

    def test_page_one_post_show_correct_context(self):
        response = self.author_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': PostViewsTest.post.id})
        )
        first_object = response.context['post']
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, f'{PostViewsTest.post.text}')
        self.assertEqual(post_author_0, f'{PostViewsTest.post.author}')
        self.assertEqual(post_group_0, f'{PostViewsTest.group.title}')
        self.assertEqual(post_image_0, f'{PostViewsTest.post.image}')

    def test_create_page_show_correct_context(self):
        response = self.author_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_update_page_show_correct_context(self):
        response = self.author_client.get(
            reverse(
                'posts:post_edit', kwargs={'post_id': PostViewsTest.post.id}
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    """Тестирование пагинатора"""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug_test',
            description='Тестовое описание',
        )
        for i in range(1, 14):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост' + str(i),
                group=cls.group
            )

    def setUp(self):
        """Неавторизованный юзер"""
        self.guest_client = Client()

        """Авторизованный юзер"""
        self.user = User.objects.create_user(username='Sereja')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        """Автор поста"""
        self.author_client = Client()
        self.author_client.force_login(PaginatorViewsTest.post.author)

    def test_first_page_ten_records(self):
        page_1 = 10
        dict_pag = {
            reverse('posts:main'): page_1,
            reverse(
                'posts:group',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            ): page_1,
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.post.author}
            ): page_1
        }

        for reverse_name, count_to_page in dict_pag.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    count_to_page
                )

    def test_second_page_three_records(self):
        page_2 = 3
        dict_pag = {
            reverse('posts:main') + '?page=2': page_2,
            reverse(
                'posts:group',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            ) + '?page=2': page_2,
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.post.author}
            ) + '?page=2': page_2
        }

        for reverse_name, count_to_page in dict_pag.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    count_to_page
                )

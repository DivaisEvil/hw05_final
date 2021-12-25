from django.test import TestCase, Client

from http import HTTPStatus

from posts.models import Group, Post, User


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_homepage(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.user = TaskURLTests.user
        self.guest_client = Client()

        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        group = TaskURLTests.group
        post = TaskURLTests.post
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{group.slug}/': 'posts/group_list.html',
            f'/profile/{post.author}/': 'posts/profile.html',
            f'/posts/{post.pk}/': 'posts/post_detail.html',
            f'/posts/{post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_task_create_url(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_list_url(self):
        """Страница /group_list_url/ доступна  пользователю."""
        group = TaskURLTests.group
        response = self.guest_client.get(f'/group/{group.slug}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail(self):
        """Страница /post_detail/ доступна  пользователю."""
        post = TaskURLTests.post
        response = self.guest_client.get(f'/posts/{post.pk}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile(self):
        """Страница /profile/ доступна  пользователю."""
        post = TaskURLTests.post
        response = self.guest_client.get(f'/profile/{post.author}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit(self):
        """Страница /edit/ доступна авторизованному пользователю."""
        post = TaskURLTests.post
        response = self.authorized_client.get(f'/posts/{post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexising_page(self):
        """Страница /unexising_page/ доступна  пользователю."""
        response = self.authorized_client.get('/unexising_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_comment_url(self):
        """комментировать посты может только авторизованный пользователь;."""
        post = TaskURLTests.post
        response = self.guest_client.get(f'/posts/{post.pk}/comment/')
        # assertRedirects перенаправление
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{post.pk}/comment/'
        )
    
    def test_user_follow_url(self):
        """Страница /follow/ доступна авторизованному пользователю."""
        user = TaskURLTests.user
        response = self.authorized_client.get(
            f'/profile/{user.username}/follow/'
        )
        self.assertRedirects(
            response,
            f'/profile/{user.username}/'
        )
        response = self.authorized_client.get(
            f'/profile/{user.username}/unfollow/'
        )
        self.assertRedirects(response, f'/profile/{user.username}/')
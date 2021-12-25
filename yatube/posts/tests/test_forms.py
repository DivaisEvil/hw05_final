import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import Client, TestCase, override_settings

from posts.forms import PostForm
from posts.models import Group, Post, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskCreateFormTests(TestCase):
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
            text='Тестовая группа',
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = TaskCreateFormTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_task(self):
        """Валидная форма создает запись в Post."""
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
        user = TaskCreateFormTests.user
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': f'{user}'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(text='Тестовый текст',
                                            author=user,).exists())

    def test_cedit_task(self):
        """Валидная форма редактирования записи в Post."""
        post = TaskCreateFormTests.post
        post_count = Post.objects.count()
        form_data = {'text': 'Отредактированый текст'}
        r = reverse('posts:post_edit', kwargs={'post_id': f'{post.pk}'})
        s = self.authorized_client.post((r), data=form_data, follow=True)
        # этот маразм r , s для автотестов
        response = s
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': f'{post.pk}'}))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(Post.objects.filter(text='Отредактированый текст',
                                            author=post.author).exists())

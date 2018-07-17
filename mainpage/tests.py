from datetime import timedelta
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.test import TestCase, Client
from . import models


HTTP_OK_STATUS = 200
HTTP_NOT_FOUND_STATUS = 404
HTTP_FOUND_STATUS = 302


class UrlsTestCase(TestCase):
    def setUp(self):
        models.Sites(name='habrahabr', url='https://habrahabr.ru/').save()
        models.Categories(headline='Все потоки', url='https://habrahabr.ru/page1/',
                          site_id=models.Sites.objects.filter(name='habrahabr').values_list('id', flat=True)[0]).save()
        self.client = Client()

    def test_wrong_url_return_http_NOT_FOUND_status(self):
        url = '/Post/ababababa'
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_NOT_FOUND_STATUS, msg='Not OK')

    def test_wrong_url_return_http_301_status(self):
        url = '/habrahabr/category/1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 301 , msg='Not OK')

    def test_wrong_url_return_http_302_status(self):
        url = '/tut/category/8/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_OK_STATUS, msg='Not OK')

    def test_profile_url_return_http_status(self):
        url = '/account/profile/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_FOUND_STATUS, msg='Not OK')

    def test_our_news_url_return_http_status(self):
        url = '/news'
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_FOUND_STATUS, msg='Not OK')

    def test_create_view_url_return_http_status(self):
        url = '/create'
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_FOUND_STATUS, msg='Not OK')

    def test_change_password_view_url_return_http_status(self):
        url = '/password_change/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_FOUND_STATUS, msg='Not OK')

    def test_login_view_url_return_http_status(self):
        url = '/login'
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_OK_STATUS, msg='Not OK')

    def test_register_view_url_return_http_status(self):
        url = '/register'
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_OK_STATUS, msg='Not OK')

    def test_logout_view_url_return_http_status(self):
        url = '/logout'
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_FOUND_STATUS, msg='Not OK')


class PostTestCase(TestCase):

    def test_create_post(self):
        models.User.objects.create_user(username='jaqombo', is_active=True, is_staff=True, is_superuser=True, password='1234')
        models.Sites(name='Name', url='mysite').save()
        models.Categories(headline='Все потоки', url='news', site_id=1).save()
        post = models.Post(title='Nazvanie', preview='Previuha', content='Soderjimoe')
        post.categories = models.Categories.objects.get(headline='Все потоки')
        post.user = models.User.objects.get(username='jaqombo')
        post.is_published = True
        post.save()
        our_post_in_db = models.Post.objects.get(title='Nazvanie')
        self.assertEqual(str(post), post.title)
        self.assertEqual(our_post_in_db.preview, post.preview)
        self.assertEqual(our_post_in_db.content, post.content)
        self.assertEqual(our_post_in_db.user, post.user)
        self.assertEqual(our_post_in_db.is_published, post.is_published)


class RegisterTestCase(TestCase):

    def test_register_process(self):
        try:
            user = models.User.objects.create(
                username='jakkemomo',
                password='12345',
                email='rofikys@mail.ru',
                is_active=False)
            user.set_password(user.password)
            from django.utils.timezone import now
            activation = models.Activation(
                valid_until=now() + timedelta(minutes=2)
            )
            activation.set_url()
            activation.save()
            user.save()
            profile = models.Profile()
            profile.activation = activation
            profile.user = user
            profile.save()
        except Exception as exc:
            raise exc
        else:
            subject = 'Подтверждение почты'
            message = user.username + ', вот ваша cсылка для активации:' + ' {url}'.format(
                url='http://' + '127.0.0.1:8000' + '/' + profile.activation.url
            )
            from_email ='jamba@support.by'
            to_list = [user.email]
            send_mail(subject, message, from_email, to_list, fail_silently=False)
            self.assertEqual(models.User.objects.filter(
                username='jakkemomo').values_list('is_active', flat=True)[0], False)  # False check
            try:
                activation = models.Activation.objects.get(url__icontains=profile.activation.url)
            except models.Activation.DoesNotExist:
                raise AssertionError
            activation.profile.user.is_active = True
            activation.profile.user.save()
            self.assertEqual(models.User.objects.filter(
                username='jakkemomo').values_list('is_active', flat=True)[0], True)  # True check


class LoginTestCase(TestCase):

    def test_login_normal_user(self):
        models.User.objects.create_user(username='Kappa', is_active=True, password='1234')
        username = 'Kappa'
        password = '1234'
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                self.assertEqual(models.User.objects.filter(username=username, is_active=True).values_list('username', flat=True)[0], username)
        else:
            print('Incorrect input')

    def test_login_wrond_user(self):
        models.User.objects.create_user(username='Kappa', is_active=True, password='1234')
        username = 'Kappa123'
        password = '1234'
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                self.assertEqual(models.User.objects.filter(username=username, is_active=True).values_list('username', flat=True)[0], username)
        else:
            try:
                self.assertNotEqual(
                    models.User.objects.filter(username=username, is_active=True).values_list('username', flat=True)[0],
                    username)
            except IndexError:
                pass

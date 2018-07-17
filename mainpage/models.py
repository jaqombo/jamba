from django.contrib.auth.models import User, AbstractUser
from django.db import models
import datetime
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

NULL_BLANK = {
    'null': True,
    'blank': True
}


# Модель номер 1. Новостные сайты
class Sites(models.Model):

    name = models.CharField(max_length=100, **NULL_BLANK)

    url = models.CharField(max_length=100, **NULL_BLANK)

    class Meta:
        verbose_name = 'Сайт'
        verbose_name_plural = 'Сайты'

    def __str__(self):
        return self.name


# Модель номер 2. Категории с этих сайтов
class Categories(models.Model):

    headline = models.CharField(max_length=100, **NULL_BLANK)

    url = models.CharField(max_length=100, **NULL_BLANK)

    site = models.ForeignKey(to='Sites', on_delete=models.CASCADE, default=12)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.headline


# Модель номер 3. Новостные посты из этих категорий
class Post(models.Model):

    url = models.SlugField(max_length=255, **NULL_BLANK)

    create_date = models.CharField(max_length=255, **NULL_BLANK,
                                   default=datetime.datetime.now().strftime('%d/%m, %H:%M'))

    publish_time = models.DateTimeField(default=now)

    is_published = models.BooleanField(default=False)

    title = models.CharField(verbose_name=_('Название'), max_length=255, **NULL_BLANK)

    preview = models.TextField(verbose_name=_('Предпросмотр'), **NULL_BLANK)

    content = models.TextField(verbose_name=_('Контент'), **NULL_BLANK)

    categories = models.ForeignKey(to='Categories', on_delete=models.CASCADE, default=999)

    pic = models.TextField(**NULL_BLANK)

    user = models.ForeignKey(to=User, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-publish_time']

    def __str__(self):
        return self.title


# Модель номер 4. Модель активации пользователя
class Activation(models.Model):
    valid_until = models.DateTimeField(
        verbose_name=_('Дата окончания действия ссылки активации'),
    )
    url = models.URLField(
        verbose_name=_('Ссылка'),
    )

    def set_url(self):
        import binascii
        import os
        self.url = 'activate/{token}/'.format(
            token=binascii.hexlify(os.urandom(10)).decode('utf-8')
        )
        pass


# Модель номер 5. Профиль пользователя
class Profile(models.Model):
    activation = models.OneToOneField(
        verbose_name=_('Активация'),
        to=Activation,
        on_delete=models.SET_NULL,
        **NULL_BLANK
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    avatar = models.ImageField(
        verbose_name=_('Аватар'),
        upload_to='.',
        **NULL_BLANK
    )

    post_fav = models.ManyToManyField(to=Post, blank=True)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __unicode__(self):
        return u'Profile of user: %s' % self.user.username



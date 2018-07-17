from django import forms
from django.contrib.auth.models import User
from . import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from .models import Profile


class UserLoginForm(forms.Form):

    username = forms.CharField(
        label=_('Имя пользователя'),
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        label=_('Пароль'),
        required=True
    )

    def clean(self):
        cleaned_data = super(UserLoginForm, self).clean().copy()

        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        user = authenticate(username=username, password=password)
        if user:
            if user.check_password(password):
                return cleaned_data
        else:
            self.add_error('password', _('Неправильный логин или пароль'))


class UserRegForm(forms.Form):

    username = forms.CharField(
        label=_('Имя пользователя'),
        required=True
    )
    email = forms.EmailField(
        label=_('Почтовый адрес'),
        required=True
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label=_('Пароль'),
        required=True
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label=_('Подтвердите пароль'),
        required=True
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                _('Пользователь с таким именем уже существует.')
            )

        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        # email2 = self.cleaned_data.get("email2")

        if email:
            # Query your UserCheckout model. Not the auth one!
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    _("Пользователь с таким эмэйлом уже существует")
                )
        return email

    # def clean_email(self):
    #
    #     email = self.cleaned_data['email']
    #     if User.objects.filter(email=email).exists():
    #         raise forms.ValidationError(
    #             _('Пользователь с таким адресом уже существует')
    #         )
    #     return email

    def clean(self, *args, **kwargs):
        cleaned_data = super(UserRegForm, self).clean().copy()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 != password2:
            # self.add_error(None, _('Пароли не совпадают'))  # none_filed_errors
            # self.add_error('password1', _('Пароли не совпадают'))
            self.add_error('password2', _('Пароли не совпадают'))
        return cleaned_data


class NewsCreate(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        return super(NewsCreate, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        kwargs['commit'] = False
        obj = super(NewsCreate, self).save(*args, **kwargs)
        if self.request:
            obj.user = self.request.user
            obj.save()
        return obj

    class Meta:
        model = models.Post
        fields = [
            'title',
            'preview',
            'content'
        ]


class NewsUpdate(forms.ModelForm):

    # title = forms.CharField(label=_('Заголовок'), widget=forms.TextInput, required=True)
    # preview = forms.CharField(label=_('Предпросмотр'), widget=forms.Textarea, required=True)
    # content = forms.CharField(label=_('Контент'), widget=forms.Textarea, required=True)

    class Meta:
        model = models.Post
        fields = [
            'title',
            'preview',
            'content',
        ]


class ProfileUpdateMETA(forms.ModelForm):
    """
    Profile Form. Composed of
    first_name,last_name,date_of_birth,gender
    """
    first_name = forms.CharField(
        label=_('Имя '),
        required=False
    )
    last_name = forms.CharField(
        label=_('Фамилия'),
        required=False
    )

    class Meta:
        model = Profile
        fields = [
            'first_name', 'last_name', 'avatar'
        ]


from datetime import timedelta
from django.contrib import messages
from django.db import transaction
from django.views.generic import DetailView, CreateView, DeleteView, View, FormView, RedirectView
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import ugettext as _

import json
from .models import User, Post
from django.views.generic import UpdateView
from . import forms
from mainpage import models as mainpage_models
import logging
log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%I:%M:%S %p')


# Profile
class ProfileView(LoginRequiredMixin, FormView):
    """
    Provides views with the current user's profile.
    """
    form_class = forms.ProfileUpdateMETA
    model = mainpage_models.Profile
    template_name = 'mainpage/profile.html'


# Profile Update Info
class ProfileUpdateView(LoginRequiredMixin, FormView):

    model = mainpage_models.Profile
    template_name = 'mainpage/profile_update.html'
    form_class = forms.ProfileUpdateMETA
    success_url = reverse_lazy('mainpage:profile')

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['first_name'] != '':
                User.objects.filter(username=request.user).update(
                    first_name=form.cleaned_data['first_name'])
            if form.cleaned_data['last_name'] != '':
                User.objects.filter(username=request.user).update(
                    last_name=form.cleaned_data['last_name'])
            if form.cleaned_data['avatar']:
                profile = mainpage_models.Profile.objects.filter(user=User.objects.get(username=request.user))
                profile.update(avatar=form.cleaned_data['avatar'])
                try:
                    form.save()
                except Exception:
                    pass
            return super(ProfileUpdateView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    # def clean_image(self, request):
    #     image = .update
    #     if image:
    #         # do some validation, if it fails
    #         raise forms.ValidationError(u'Form error')
    #     return image

    # def post(self, request, *args, **kwargs):
    #     form = self.get_form()
    #     if form.is_valid():
    #         with transaction.atomic():
    #             try:
    #                 user = User.objects.get(username=request.user)
    #                 User.objects.create(
    #                     first_name=form.cleaned_data['first_name'],
    #                     last_name=form.cleaned_data['last_name'])
    #                 user.save()
    #
    #                 profile = mainpage_models.Profile()
    #                 profile.avatar = form.cleaned_data['avatar']
    #                 profile.save()
    #             except Exception as exc:
    #                 raise exc
    #         return self.form_valid(form)
    #     return self.form_invalid(form)


# Profile Favorite Section
class ProfileFavourites(LoginRequiredMixin, FormView):
    form_class = forms.ProfileUpdateMETA
    model = mainpage_models.Profile
    template_name = 'mainpage/favourites.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = mainpage_models.Profile(user=self.request.user)
        favourite_posts = mainpage_models.Profile.objects.filter(post_fav__profile=current_user)
        for item in favourite_posts:
            context['favourite_posts'] = item.post_fav.all()
        context['profile'] = mainpage_models.Profile.objects.all()
        return context


# News Details
class PostDetailView(DetailView):  # детализированное представление модели

    model = mainpage_models.Post
    # form_class = forms.ProfileFavPost
    template_name = 'mainpage/post_detail.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = mainpage_models.Profile.objects.all()
        try:
            for item in mainpage_models.Profile.objects.filter(user=self.request.user):
                # print(item.post_fav.all().values_list('id', flat=True))
                context['favs'] = item.post_fav.all().values_list('id', flat=True)
        except TypeError:
            pass
        return context


# News Create
class NewsCreateView(LoginRequiredMixin, CreateView):
    model = mainpage_models.Post
    form_class = forms.NewsCreate
    template_name = 'mainpage/news_create.html'
    success_url = reverse_lazy('mainpage:custom_posts')

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        # form.instance.user = Post.objects.get(user=current_user)
        if form.is_valid():
            if request.user is not None:
                post = Post()
                post.title = form.cleaned_data['title']
                post.preview = form.cleaned_data['preview']
                post.content = form.cleaned_data['content']
                post.user = request.user
                post.save()
                messages.success(
                    self.request,
                    _('Пост успешно создан и отправлен на модерацию.')
                )
            return self.form_valid(form)
        else:
            messages.error(
                self.request,
                _('Пост не был создан. Попробуйте снова.')
            )
            return self.form_invalid(form)


# News Update
class NewsUpdateView(LoginRequiredMixin, UpdateView):
    model = mainpage_models.Post
    template_name = 'mainpage/news_update.html'
    form_class = forms.NewsUpdate
    success_url = reverse_lazy('mainpage:custom_posts')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user == request.user or request.user.is_staff:
            return super().get(request, *args, **kwargs)
        else:
            raise Http404


# News Delete
class NewsDeleteView(LoginRequiredMixin, DeleteView):
    model = mainpage_models.Post
    success_url = reverse_lazy('mainpage:custom_posts')
    template_name = 'mainpage/post_confirm_delete.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user == request.user or request.user.is_staff:
            return render(request, self.template_name, {'object': self.object})
        else:
            raise Http404  # or return HttpResponse('404_url')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user == request.user or request.user.is_staff:
            self.object.delete()
            return redirect('mainpage:custom_posts')
        else:
            raise Http404  # or return HttpResponse('404_url')


# Our news
class CustomPostView(LoginRequiredMixin, FormView):

    model = mainpage_models.Post
    template_name = 'mainpage/our_news.html'

    def get_context_data(self, **kwargs):
        return {'post_items': mainpage_models.Post.objects.filter(
            categories__headline='Наши новости').filter(
            is_published=True)}


# Moderation news
class NewsOnModerationView(LoginRequiredMixin, FormView):

    model = mainpage_models.Post
    template_name = 'mainpage/posts_on_moderation.html'

    def get_context_data(self, **kwargs):
        return {'post_items': mainpage_models.Post.objects.filter(
            categories__headline='Наши новости', is_published=False)}


# Register
class UserRegister(FormView):
    form_class = forms.UserRegForm
    template_name = 'mainpage/registration_form.html'
    success_url = reverse_lazy('mainpage:login')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():

            with transaction.atomic():
                try:
                    user = mainpage_models.User.objects.create(
                        username=form.cleaned_data['username'],
                        password=form.cleaned_data['password2'],
                        email=form.cleaned_data['email'],
                        is_active=False)
                    user.set_password(user.password)
                    from django.utils.timezone import now
                    activation = mainpage_models.Activation(
                        valid_until=now() + timedelta(minutes=2)
                    )
                    activation.set_url()
                    activation.save()
                    user.save()
                    profile = mainpage_models.Profile()
                    profile.activation = activation
                    profile.user = user
                    profile.save()
                except Exception as exc:
                    messages.error(
                        self.request,
                        _('Не удалось создать учётную запись. Обратитесь к администратору.')
                    )
                    raise exc
                else:
                    messages.success(
                        request,
                        _('Учётная запись создана. Уведомление для активации в ящике.')
                    )

                    # send_mail(subject, message, from_email, to_list, fail_silently=True)
                    subject = _('Подтверждение почты')
                    message = user.username + _(', вот ваша cсылка для активации:') + ' {url}'.format(
                                    url='http://' + self.request.META['HTTP_HOST'] + '/' + profile.activation.url
                                )
                    from_email = settings.EMAIL_HOST_USER + '@yandex.ru'
                    to_list = [user.email]
                    send_mail(subject, message, from_email, to_list, fail_silently=False)
                    # send_activation_email(profile, self.request.META['HTTP_HOST'])
                # username = form.cleaned_data['username']
                # password = form.cleaned_data['password2']
                #
                # user = authenticate(username=username, password=password)
                # if user is not None:
                #     if user.is_active:
                #         login(request, user)
                #         # profile = mainpage_models.Profile.objects.create(
                #         #     valid_until=now() + ..
                #         # )
                return self.form_valid(form)
        return self.form_invalid(form)


# Activate account during registration if token in url
class ActivateView(RedirectView):
    url = reverse_lazy('mainpage:login')

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        try:
            activation = mainpage_models.Activation.objects.get(url__icontains=token)
        except mainpage_models.Activation.DoesNotExist:
            messages.error(
                request,
                _('Не удалось активировать учётную запись.')
            )
            return redirect('mainpage:register')

        activation.profile.user.is_active = True
        activation.profile.user.save()

        return super(ActivateView, self).get(request, *args, **kwargs)


# Login
class UserLogin(View):
    form_class = forms.UserLoginForm
    template_name = 'mainpage/login_form.html'

    def get(self, request):
        form = self.form_class(None)

        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('mainpage:home')
            else:
                print('Incorrect input')
        return render(request, self.template_name, {'form': form})


# Main function for showing posts on categories
def categories(request, slug):
    context = {
        'post_items': mainpage_models.Post.objects.filter(categories=slug),
        'category_items': mainpage_models.Categories.objects.filter(pk=slug),
    }
    return render(request, 'mainpage/home.html', context)


# Favorite button
@login_required
def favorite_toggle(request):
    favorited = False
    if request.method == 'POST':
        pk = request.POST['pk']
        profile = mainpage_models.Profile(user=request.user)
        fav = mainpage_models.Post.objects.filter(id=pk).values_list('id', flat=True)[0]
        if fav in profile.post_fav.all().values_list('id', flat=True):
            profile.post_fav.remove(fav)
            profile.save()
        else:
            favorited = True
            profile.post_fav.add(fav)
            profile.save()

    info = {'favorited': favorited}
    return HttpResponse(json.dumps(info), content_type="application/json")


# Publish button
@login_required
def moderator_toggle(request):
    published = False
    if request.method == 'POST':
        pk = request.POST['pk']
        moderated_post = mainpage_models.Post.objects.filter(id=pk)
        if mainpage_models.Post.objects.filter(id=pk).values_list('is_published', flat=True)[0]:
            moderated_post.update(is_published=False)
        else:
            published = True
            moderated_post.update(is_published=True)
    info = {'is_published': published}
    return HttpResponse(json.dumps(info), content_type="application/json")


# Logout
def logout_view(request):
    logout(request)
    return redirect('mainpage:home')


# Redirect function to habr posts
def push_to_news(request):
    page_num = mainpage_models.Categories.objects.filter(headline='Все потоки').values('id')[0]['id']
    url = 'http://127.0.0.1:8000/habrahabr/category/'+str(page_num)
    return redirect(url)


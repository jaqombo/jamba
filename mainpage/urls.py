from django.urls import path
from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views


app_name = 'mainpage'

urlpatterns = [

    # http://127.0.0.1:8000/
    path('', views.push_to_news, name='home'),

    # /habrahabr/category/3/
    url('habrahabr/category/(?P<slug>[\w-]+)/$', views.categories, name='habr_list'),

    # /tut/category/9/
    url('tut/category/(?P<slug>[\w-]+)/$', views.categories, name='tut_list'),

    # habrahabr/category/3/post/1910
    url(r'^(habrahabr|tut)/category/(?P<slug>[\w-]+)/post/(?P<pk>\d+)/$', views.PostDetailView.as_view(),
        name='news_detail'),

    # post/1910
    url(r'^post/(?P<pk>\d+)/$', views.PostDetailView.as_view(), name='post'),

    # /create
    path('create', views.NewsCreateView.as_view(), name='news_create'),

    # post/1910/update
    url(r'^post/(?P<pk>\d+)/update$', views.NewsUpdateView.as_view(), name='news_update'),

    # post/1910/delete
    url(r'^post/(?P<pk>\d+)/delete$', views.NewsDeleteView.as_view(), name='news_delete'),

    path('register', views.UserRegister.as_view(), name='register'),

    path('login', views.UserLogin.as_view(), name='login'),

    path('logout', views.logout_view, name='logout'),

    path('news', views.CustomPostView.as_view(), name='custom_posts'),

    path('moderating', views.NewsOnModerationView.as_view(), name='posts_on_moderation'),

    path('activate/<str:token>/', views.ActivateView.as_view(), name='activate'),

    url(r'^account/profile/favourites/post/(?P<pk>\d+)/$', views.PostDetailView.as_view(), name='post_favours'),

    url(r'user/favorited$', views.favorite_toggle, name='fav_toggle'),

    url(r'user/moderated$', views.moderator_toggle, name='mod_toggle'),

    url(r'^account/profile/favourites/$', views.ProfileFavourites.as_view(),
      name='favourites'),

    path('account/profile/update', views.ProfileUpdateView.as_view(), name='update_profile'),

    url(r'account/profile', views.ProfileView.as_view(), name='profile'),


    url(r'password_change/$', auth_views.PasswordChangeView.as_view(template_name='mainpage/change-password.html',
                                                       success_url='/accounts/password_change_done'),
        name='change_password'),

    url(r'password_change_done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='mainpage/password_change_done.html'),
        name='change_password_done'),

    url(r'password_reset/$',
        auth_views.PasswordResetView.as_view(
            template_name='mainpage/registration/password_reset_form.html',
            email_template_name='mainpage/registration/password_reset_email.html',
            subject_template_name='mainpage/registration/password_reset_subject.txt',
            success_url='/accounts/password_reset_done/', from_email='support@jamba.by'),
        name='password_reset'),

    url(r'password_reset_done/',
        auth_views.PasswordResetDoneView.as_view(template_name='mainpage/registration/password_reset_done.html')),

    url(r'password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name='mainpage/registration/password_reset_confirm.html',
                                                    success_url='/accounts/password_reset_complete/'),
        name='password_reset_confirm'),

    url(r'password_reset_complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='mainpage/registration/password_reset_complete.html')),



]


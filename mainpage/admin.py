from django.contrib import admin
from mainpage.models import Post, Profile


class NewsAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'create_date'
    ]
    ordering = ['-create_date']


class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'avatar',
    ]


admin.site.register(Profile, ProfileAdmin)

admin.site.register(Post, NewsAdmin)


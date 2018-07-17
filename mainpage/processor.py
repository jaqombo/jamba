from .models import Categories


def first_num_for_menu(request):
    return {'a': Categories.objects.filter(headline='Все потоки').get()}
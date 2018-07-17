import urllib.request
import bs4 as bs
from bs4 import BeautifulSoup
import requests
import django
import sys
import os
import datetime
from datetime import date, timedelta
from mysite.settings import SETTINGS_PATH

project_dir = SETTINGS_PATH

sys.path.append(project_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

django.setup()

from mainpage.models import Sites, Categories, Post, Profile
from django.contrib.auth.models import User


User.objects.create_user(username='jaqombo', email='spat123@mail.ru', is_active=True, is_staff=True, is_superuser=True, password='1234')
Profile.objects.create(user=User.objects.get(username='jaqombo'))


# Шаг 1 - Добавление сайтов в модель источника
def sites_to_model():
    print('Adding sites to models..')
    Sites.objects.create(name='habrahabr', url='https://habrahabr.ru/')
    # Sites.objects.create(name='Onliner', url='https://news.tut.by/')
    Sites.objects.create(name='TUT.BY', url='https://news.tut.by/')
    # Sites.objects.create(name='DEV.BY', url='https://news.tut.by/')
    Sites.objects.create(name='Jamba', url='/custom_posts', id=999)
    print('Sites added successfully.')
    print('-'*40)


# Шаг 2 - Хабровские категории
def habr_categories_to_model():

    # Парсинг категорий с главной страницы хабра и загрузка их в модель категорий
    print('Habr categories uploading..')
    url = 'https://habrahabr.ru/'
    sause = requests.get(url)
    soup = BeautifulSoup(sause.content, "lxml")

    category_names = []
    category_urls = []
    category_list = soup.find('div', class_='dropdown-container dropdown-container_flows')
    category_items = category_list.find_all('li', class_='n-dropdown-menu__item')
    Categories.objects.create(headline='Наши новости', url='/custom_posts',
                              site_id=999, id=999)
    Categories.objects.create(headline='Все потоки', url='https://habrahabr.ru/page1/',
                              site_id=Sites.objects.filter(name='habrahabr').values('id')[0]['id'])
    for item in category_items:
        category = Categories()
        category_name = item.find('a').text
        category_url = item.find('a').get('href')
        category_names.append(category_name.encode('utf-8'))
        category_urls.append(category_url.encode('utf-8'))
        category.headline = category_names.pop(0).decode()
        category.url = category_urls.pop(0).decode()
        category.site = Sites.objects.get(name='habrahabr', url='https://habrahabr.ru/')
        category.save()
    print('Habr categories imported successfully.')
    print('-'*40)


# Шаг 3 - Главная страница хабра как последняя категория и загрузка постов
def data_import_habr():
    print('Habr posts collecting..')
    url = 'https://habrahabr.ru/'
    sause = requests.get(url)
    soup = BeautifulSoup(sause.content, "lxml")

    # Парсинг главной страницы как отдельной категории "Все потоки"

    urls = []
    titles = []
    times = []
    prev_text = []
    content = []

    item_list = soup.find('ul', {'class': "content-list content-list_posts shortcuts_items"})
    # <class 'bs4.element.Tag'>

    items = item_list.find_all('li', class_="content-list__item content-list__item_post shortcuts_item")
    # <class 'bs4.element.ResultSet'>

    for item in items:
        try:
            post_url = item.find('article', {'class': 'post post_preview'}).find('h2').find('a').get('href')
            post_name = item.find('article', {'class': 'post post_preview'}).find('h2').find('a').text
            post_time = item.find('article', {'class': 'post post_preview'}).find('header').\
                find('span', class_="post__time").text
            post_preview = item.find('article', {'class': 'post post_preview'}).\
                find('div', {'class': 'post__text post__text-html js-mediator-article'})

            urls.append(post_url.encode('utf-8'))

            titles.append(post_name.encode('utf-8'))

            times.append(post_time.encode('utf-8'))

            prev_text.append(post_preview.encode('utf-8'))

        except (AttributeError, IndexError):
            pass

    # Парсинг содержимого постов c главной страницы и загрузка в модели

    links = soup('a', class_="post__title_link")
    for link in links:
        sause = urllib.request.urlopen(link.get('href')).read()
        soup = bs.BeautifulSoup(sause, 'lxml')
        for data in soup.find_all('div', class_="post__text post__text-html js-mediator-article"):
            content.append(data.encode('utf-8'))
        post = Post()
        try:
            post.url = urls.pop(0).decode()
            post.title = titles.pop(0).decode()
            post.create_date = times.pop(0).decode()
            post.preview = prev_text.pop(0).decode()
            post.content = content.pop(0).decode()
            post.categories = Categories.objects.get(headline='Все потоки')
            post.user = User.objects.get(username='jaqombo')
            post.is_published = True
            post.save()
        except IndexError:
            pass

    # Парсинг категорий

    category_urls = ['https://habrahabr.ru/flows/develop/best', 'https://habrahabr.ru/flows/admin/best',
                     'https://habrahabr.ru/flows/design/best', 'https://habrahabr.ru/flows/management/best',
                     'https://habrahabr.ru/flows/marketing/best', 'https://habrahabr.ru/flows/misc/best'
                     ]

    n = Categories.objects.filter(headline='Все потоки', url='https://habrahabr.ru/page1/').values('id')[0]['id']
    # Номер первой категории в модели формата n-1
    for url in category_urls:

        sause = requests.get(url)
        soup = BeautifulSoup(sause.content, 'lxml')

        n += 1      # Номер первой категории в модели
        # Парсинг страницы

        urls = []
        titles = []
        times = []
        prev_text = []
        content = []

        item_list = soup.find('ul', {'class': "content-list shortcuts_items"})
        # <class 'bs4.element.Tag'>

        items = item_list.find_all('li', class_="content-list__item content-list__item_post shortcuts_item")
        # <class 'bs4.element.ResultSet'>

        for item in items:
            try:
                post_url = item.find('article', {'class': 'post post_preview'}).find('h2').find('a').get('href')
                post_name = item.find('article', {'class': 'post post_preview'}).find('h2').find('a').text
                post_time = item.find('article', {'class': 'post post_preview'}).find('header').\
                    find('span', class_="post__time").text
                post_preview = item.find('article', {'class': 'post post_preview'}).\
                    find('div', {'class': 'post__text post__text-html js-mediator-article'})
                urls.append(post_url.encode('utf-8'))
                titles.append(post_name.encode('utf-8'))
                times.append(post_time.encode('utf-8'))
                prev_text.append(post_preview.encode('utf-8'))
            except (AttributeError, IndexError):
                pass

        # Парсинг содержимого постов и загрузка в модели

        links = soup('a', class_="post__title_link")
        for link in links:
            sause = urllib.request.urlopen(link.get('href')).read()
            soup = bs.BeautifulSoup(sause, 'lxml')
            for data in soup.find_all('div', class_="post__text post__text-html js-mediator-article"):
                content.append(data.encode('utf-8'))
            post = Post()
            try:
                post.url = urls.pop(0).decode()
                post.title = titles.pop(0).decode()
                post.create_date = times.pop(0).decode()
                post.preview = prev_text.pop(0).decode()
                post.content = content.pop(0).decode()
                post.categories = Categories.objects.get(id=n)
                post.user = User.objects.get(username='jaqombo')
                post.is_published = True
                post.save()
            except IndexError:
                pass

    print('Habr posts collecting is finished.')
    print('-'*40)

    # Отдельный парсинг хабов и загрузка в модели
    #
    # ids = []
    # categ_name = []
    # categ_url = []
    #
    # iid_list = Post.objects.values_list('pk', flat=True)
    # for item in iid_list:
    #     ids.append(item)
    #
    # crops = item_list.find_all('ul', class_="post__hubs inline-list")
    #
    # for one in crops:
    #     category = Categories()
    #     again = one.findChildren()
    #     ID = ids.pop(0)
    #
    #     for one_category in again:
    #         try:
    #             cat = one_category.find('a').text
    #             cat_url = one_category.find('a').get('href')
    #
    #             categ_name.append(cat.encode('utf-8'))
    #             categ_url.append(cat_url.encode('utf-8'))
    #
    #             category = Categories.objects.create(headline=categ_name.pop(0).decode(), url=categ_url.pop(0).
    # decode(),
    #                                                  posts_id=ID)
    #         except AttributeError:
    #             pass
    #     category.save()


# Шаг 4 - Тутбаевские категории
def tut_categories_to_model():
    # Парсинг категорий с главной страницы и загрузка их в модель категорий
    print('Tut.by categories uploading..')
    url = 'https://news.tut.by/'
    sause = requests.get(url)
    soup = BeautifulSoup(sause.content, "lxml")

    category_names = []
    category_urls = []
    category_list = soup.find('ul', class_='b-nav-list')
    category_items = category_list.find_all('li')
    n=8
    for item in category_items:
        category = Categories()
        n -= 1
        if n > 0:
            try:
                category_name = item.find('a').text
                category_url = item.find('a').get('href')
                category_names.append(category_name.encode('utf-8'))
                category_urls.append(category_url.encode('utf-8'))
            except AttributeError:
                pass
        try:
            category.headline = category_names.pop(0).decode()
            category.url = category_urls.pop(0).decode()
            category.site = Sites.objects.get(name='TUT.BY', url='https://news.tut.by/')
            category.save()
        except IndexError:
            pass
    print('Tut.by categories imported successfully.')
    print('-'*40)


# Шаг 5 - Загрузка  постов с тут бая
def data_import_tut():
    print('Tut.by posts collecting..')

    category_urls = ['https://news.tut.by/daynews/', 'https://news.tut.by/geonews/minsk/',
                     'https://news.tut.by/top5news/', 'https://news.tut.by/economics/',
                     'https://news.tut.by/society/', 'https://news.tut.by/world/', 'https://news.tut.by/culture/']

    n = Categories.objects.filter(headline='Главное', url='https://news.tut.by/daynews/').values('id')[0]['id'] - 1
    # Номер первой категории в модели формата n-1
    for url in category_urls:
        sause = requests.get(url)
        soup = BeautifulSoup(sause.content, 'lxml')

        n += 1      # Номер первой категории в модели

    #     # Парсинг страницы

        urls = []
        titles = []
        times = []
        prev = []
        post_pics = []
        content = []

        post_list = soup.find('div', class_="col-w")

        items = post_list.find_all('div', class_="news-entry big annoticed time ni")

        for item in items:
            try:
                post_url = item.find('a').get('href')
                post_name = item.find('span', {'class': 'entry-head'}).text
                post_time = item.find('span', {'class': 'entry-meta'}).find('span', {'class': 'entry-time'}).find('span').text
                post_preview = item.find('span', {'class': 'entry-note'}).text
                post_pic = item.find('span', {'class': 'entry-pic'})
                urls.append(post_url.encode('utf-8'))
                titles.append(post_name.encode('utf-8'))
                times.append(post_time.encode('utf-8'))
                prev.append(post_preview.encode('utf-8'))
                post_pics.append(post_pic.encode('utf-8'))
            except (AttributeError, IndexError):
                pass

        # Парсинг содержимого постов и загрузка в модели

        links = soup('div', class_="news-entry big annoticed time ni")
        for link in links:
            url = link.next_element.get('href')
            sause = requests.get(url)
            soup = BeautifulSoup(sause.content, 'lxml')
            for data in soup.find_all('div', class_="js-mediator-article"):
                content.append(data.encode('utf-8'))
            post = Post()
            try:
                post.url = urls.pop(0).decode()
                post.title = titles.pop(0).decode()
                post.create_date = times.pop(0).decode()
                post.preview = prev.pop(0).decode()
                post.pic = post_pics.pop(0).decode()
                post.content = content.pop(0).decode()
                post.categories = Categories.objects.get(id=n)
                post.user = User.objects.get(username='jaqombo')
                post.is_published = True
                post.save()
            except IndexError:
                pass
    print('Tut by posts collecting is finished.')
    print('-'*40)


# Шаг 6 - Смена даты у всех постов в приемлимый вид
def change_post_time():
    print('Changing post time to a normal representation..')

    RU_MONTH_VALUES = {
        'января': 1,
        'февраля': 2,
        'марта': 3,
        'апреля': 4,
        'мая': 5,
        'июня': 6,
        'июля': 7,
        'августа': 8,
        'сентября': 9,
        'октября': 10,
        'ноября': 11,
        'декабря': 12,
        'сегодня': date.today(),
        'вчера': date.today()-timedelta(1)
    }

    def int_value_from_ru_month(date_str):
        for k, v in RU_MONTH_VALUES.items():
            date_str = date_str.replace(k, str(v))
        return date_str

    date_string = [e.create_date for e in Post.objects.all()]

    for date_str in date_string:
        date_string = int_value_from_ru_month(date_str)
        try:
            d = datetime.datetime.strptime(date_string, '%Y-%m-%d в %H:%M').strftime('%d/%m, %H:%M')
            Post.objects.filter(create_date=date_str).update(create_date=d)
        except ValueError:
            pass
            try:
                d = datetime.datetime.strptime(date_string, '%Y-%m-%d в %H:%M').strftime('%d/%m, %H:%M')
                Post.objects.filter(create_date=date_str).update(create_date=d)
            except ValueError:
                pass
                try:
                    d = datetime.datetime.strptime(date_string, '%d %m %Y в %H:%M').strftime('%d/%m, %H:%M')
                    Post.objects.filter(create_date=date_str).update(create_date=d)
                except ValueError:
                    pass
                    try:
                        d = datetime.datetime.strptime(date_string, '%d %m в %H:%M').strftime('%d/%m, %H:%M')
                        Post.objects.filter(create_date=date_str).update(create_date=d)
                    except ValueError:
                        pass
                        try:
                            d = datetime.datetime.strptime(date_str, '%d %m %Y в %H:%M').strftime('%d %B %Y, %H:%M')
                            Post.objects.filter(create_date=date_str).update(create_date=d)
                        except ValueError:
                            pass
    print('Time field of the posts changed successfully.')
    print('-'*40)
    print('Success')


sites_to_model()
habr_categories_to_model()
data_import_habr()
tut_categories_to_model()
data_import_tut()
change_post_time()



import datetime
import urllib.request
import bs4 as bs
from bs4 import BeautifulSoup
import requests
import django
import sys
import os
import time
from mysite.settings import SETTINGS_PATH

start_time = time.time()

project_dir = SETTINGS_PATH

sys.path.append(project_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

django.setup()

from mainpage.models import Categories, Post
from django.contrib.auth.models import User

if User.objects.get(username='jaqombo'):
    pass
else:
    User.objects.create_user(username='jaqombo', is_active=True, is_staff=True, is_superuser=True, password='1234')


# Добавление уникальных постов для всех категорий Habrahabr.ru
def dataimporthabr():
    category_names = ['Все потоки', 'Разработка', 'Администрирование', 'Дизайн', 'Управление', 'Маркетинг', 'Разное']
    for slug in category_names:
        category_link = Categories.objects.filter(headline=slug).values('url')[0]['url']
        print(category_link)
        k = 0
        g = 1
        urls = []
        titles = []
        times = []
        prev_text = []
        content = []
        while k < 10:
            url = category_link + 'page' + str(g)
            g += 1
            sause = requests.get(url)
            soup = BeautifulSoup(sause.content, "lxml")

            item_list = soup.find('div', {'class': "posts_list"})

            try:
                items = item_list.find_all('li', class_="content-list__item content-list__item_post shortcuts_item")
                # <class 'bs4.element.ResultSet'>
            except AttributeError:
                break
            n = 0
            for item in items:
                try:
                    post_url = item.find('article', {'class': 'post post_preview'}).find('h2').find('a').get('href')
                    post_name = item.find('article', {'class': 'post post_preview'}).find('h2').find('a').text
                    if Post.objects.filter(url=post_url, title=post_name, categories__headline=slug).exists():
                        print('Skipping post that is already in this category')
                        break
                    else:
                        k += 1
                        print(post_url)
                        if k == 10:
                            break
                        post_time = item.find('article', {'class': 'post post_preview'}).find('header').\
                            find('span', class_="post__time").text
                        post_preview = item.find('article', {'class': 'post post_preview'}).\
                            find('div', {'class': 'post__text post__text-html js-mediator-article'})
                        urls.append(post_url.encode('utf-8'))
                        titles.append(post_name.encode('utf-8'))
                        times.append(post_time.encode('utf-8'))
                        prev_text.append(post_preview.encode('utf-8'))
                        n += 1
                        continue
                except (AttributeError, IndexError):
                    pass
            print('Page ', g-1, ' parsed successfully.')
            print('Number of unique posts: ', k)

        if k == 0:
            print('Unique posts for this category don`t exist yet')
            pass
        else:
            # Парсинг содержимого постов c главной страницы и загрузка в модели
            for url in urls:
                sause = urllib.request.urlopen(url.decode()).read()
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
                    post.categories = Categories.objects.get(headline=slug)
                    post.user = User.objects.get(username='jaqombo')
                    post.is_published = True
                    post.save()
                except IndexError:
                    pass


# Добавление уникальных постов для всех категорий TUT.BY
def dataimporttut():
    category_names = ['Главное', 'Минск', 'Эксклюзив', 'Деньги и власть', 'Общество', 'В мире', 'Кругозор']
    n = Categories.objects.filter(headline='Главное', url='https://news.tut.by/daynews/').values('id')[0]['id'] - 1
    for slug in category_names:
        category_link = Categories.objects.filter(headline=slug).values('url')[0]['url']
        k = 0
        g = 1
        n += 1
        urls = []
        titles = []
        times = []
        prev = []
        post_pics = []
        content = []

        while k < 10:
            url = category_link + str(g)
            print(url)
            g += 1
            sause = requests.get(url)
            soup = BeautifulSoup(sause.content, "lxml")
            post_list = soup.find('div', class_="col-w")
            items = post_list.find_all('div', class_="news-entry big annoticed time ni")
            for item in items:
                try:
                    post_url = item.find('a').get('href')
                    post_name = item.find('span', {'class': 'entry-head'}).text
                    if Post.objects.filter(url=post_url, categories__headline=slug).exists():
                        print('Skipping post that is already in this category')
                        break
                    else:
                        k += 1
                        print(post_url)
                        if k == 10:
                            break
                        post_time = item.find('span', {'class': 'entry-meta'}).find('span',
                                                                                    {'class': 'entry-time'}).find(
                            'span').text
                        post_preview = item.find('span', {'class': 'entry-note'}).text
                        post_pic = item.find('span', {'class': 'entry-pic'})

                        urls.append(post_url.encode('utf-8'))

                        titles.append(post_name.encode('utf-8'))

                        times.append(post_time.encode('utf-8'))

                        prev.append(post_preview.encode('utf-8'))

                        post_pics.append(post_pic.encode('utf-8'))
                        continue

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
                    post.categories = Categories.objects.get(headline=slug)
                    post.user = User.objects.get(username='jaqombo')
                    post.is_published = True
                    post.save()
                except IndexError:
                    pass
        print('Tut by posts collecting is finished.')
        print('-' * 40)


# Приведение времени к нормальному типу
def timefix():
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
        'сегодня': datetime.date.today(),
        'вчера': datetime.date.today() - datetime.timedelta(1)
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


print("--- %s seconds ---" % (time.time() - start_time))

dataimporthabr()
dataimporttut()























# Generated by Django 2.0.1 on 2018-07-17 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0004_auto_20180717_2138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='create_date',
            field=models.CharField(blank=True, default='17/07, 21:44', max_length=255, null=True),
        ),
    ]

# Generated by Django 2.2.7 on 2019-11-27 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie_ratings', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='movie',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='rating',
            name='rating',
            field=models.IntegerField(),
        ),
    ]

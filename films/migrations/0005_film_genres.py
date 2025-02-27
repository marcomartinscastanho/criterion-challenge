# Generated by Django 5.1.5 on 2025-01-26 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_genre'),
        ('films', '0004_film_tmdb_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='genres',
            field=models.ManyToManyField(related_name='films', to='common.genre'),
        ),
    ]

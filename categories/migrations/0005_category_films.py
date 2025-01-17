# Generated by Django 5.1.5 on 2025-01-17 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0004_remove_category_films_delete_filmcategory'),
        ('films', '0002_film_directors'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='films',
            field=models.ManyToManyField(related_name='categories', to='films.film'),
        ),
    ]

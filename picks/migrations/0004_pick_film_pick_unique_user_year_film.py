# Generated by Django 5.1.5 on 2025-01-17 18:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0007_category_films'),
        ('films', '0012_film_directors'),
        ('picks', '0003_remove_pick_unique_user_year_film_remove_pick_film'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='pick',
            name='film',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='picks', to='films.film'),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='pick',
            constraint=models.UniqueConstraint(fields=('user', 'year', 'film'), name='unique_user_year_film'),
        ),
    ]

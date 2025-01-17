# Generated by Django 5.1.5 on 2025-01-17 03:16

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('categories', '0001_initial'),
        ('films', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Pick',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(2020)])),
                ('watched', models.BooleanField(default=False)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='picks', to='categories.category')),
                ('film', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='picks', to='films.film')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='picks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('user', 'category'), name='unique_user_category'), models.UniqueConstraint(fields=('user', 'year', 'film'), name='unique_user_year_film')],
            },
        ),
    ]

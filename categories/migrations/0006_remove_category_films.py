# Generated by Django 5.1.5 on 2025-01-17 18:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0005_category_films'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='films',
        ),
    ]

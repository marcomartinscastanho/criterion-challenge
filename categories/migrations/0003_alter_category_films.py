# Generated by Django 5.1.5 on 2025-01-17 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0002_category_custom_criteria'),
        ('films', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='films',
            field=models.ManyToManyField(blank=True, related_name='categories', to='films.film'),
        ),
    ]

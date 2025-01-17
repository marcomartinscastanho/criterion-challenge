# Generated by Django 5.1.5 on 2025-01-17 17:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('films', '0006_film_cc_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='film',
            name='year',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1870)]),
        ),
    ]

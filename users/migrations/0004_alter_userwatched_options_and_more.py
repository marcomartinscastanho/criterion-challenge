# Generated by Django 5.1.5 on 2025-01-20 19:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_userwatched_userwatchlist'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userwatched',
            options={'verbose_name': 'User Watched List', 'verbose_name_plural': 'Watched Films'},
        ),
        migrations.AlterModelOptions(
            name='userwatchlist',
            options={'verbose_name': 'User Watchlist', 'verbose_name_plural': 'Watchlisted Films'},
        ),
    ]

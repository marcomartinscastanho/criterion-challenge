# Generated by Django 5.1.5 on 2025-01-17 20:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("categories", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="category", name="custom_criteria", field=models.JSONField(blank=True, null=True)
        ),
    ]

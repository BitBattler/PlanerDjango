# Generated by Django 5.0.4 on 2024-05-09 18:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Terrassenplaner', '0018_farbe_kategorie_farbe'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='farbe',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Terrassenplaner.farbe'),
        ),
    ]

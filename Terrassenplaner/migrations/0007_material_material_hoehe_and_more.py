# Generated by Django 5.0.4 on 2024-04-21 10:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Terrassenplaner', '0006_material_rohstoff'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='material_hoehe',
            field=models.DecimalField(decimal_places=4, default=0.04, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='material',
            name='material_breite',
            field=models.DecimalField(decimal_places=4, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)]),
        ),
        migrations.AlterField(
            model_name='material',
            name='material_laenge',
            field=models.DecimalField(decimal_places=4, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)]),
        ),
    ]

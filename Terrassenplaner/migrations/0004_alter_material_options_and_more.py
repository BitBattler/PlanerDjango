# Generated by Django 5.0.4 on 2024-04-19 20:58

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Terrassenplaner', '0003_material_breite_material_laenge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='material',
            options={'ordering': ['material_name'], 'verbose_name': 'Material', 'verbose_name_plural': 'Materialien'},
        ),
        migrations.RenameField(
            model_name='material',
            old_name='name',
            new_name='material_name',
        ),
        migrations.RemoveField(
            model_name='material',
            name='breite',
        ),
        migrations.RemoveField(
            model_name='material',
            name='kategorie',
        ),
        migrations.RemoveField(
            model_name='material',
            name='laenge',
        ),
        migrations.RemoveField(
            model_name='material',
            name='price_per_unit',
        ),
        migrations.RemoveField(
            model_name='material',
            name='unit',
        ),
        migrations.RemoveField(
            model_name='material',
            name='unit_size',
        ),
        migrations.AddField(
            model_name='material',
            name='material_breite',
            field=models.DecimalField(decimal_places=2, default=0.06, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='material',
            name='material_kategorie',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='materialien', to='Terrassenplaner.kategorie'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='material',
            name='material_laenge',
            field=models.DecimalField(decimal_places=2, default=2.9, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='material',
            name='material_price_per_unit',
            field=models.DecimalField(decimal_places=2, default=15.15, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)]),
            preserve_default=False,
        ),
    ]

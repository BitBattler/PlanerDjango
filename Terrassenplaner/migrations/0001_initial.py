# Generated by Django 5.0.4 on 2024-04-19 10:13

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Kategorie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100)),
                ('price_per_unit', models.DecimalField(decimal_places=2, help_text='Preis pro Einheit in der gewählten Währung', max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('unit', models.CharField(help_text='Maßeinheit, z.B. Meter, Kilogramm etc.', max_length=20)),
                ('kategorie', models.ForeignKey(help_text='Kategorie, zu der das Material gehört', on_delete=django.db.models.deletion.CASCADE, related_name='materialien', to='Terrassenplaner.kategorie')),
            ],
            options={
                'verbose_name': 'Material',
                'verbose_name_plural': 'Materialien',
                'ordering': ['name'],
            },
        ),
    ]

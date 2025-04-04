# Generated by Django 5.2a1 on 2025-04-04 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pokemon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pokedex', models.IntegerField()),
                ('name', models.CharField(max_length=50)),
                ('primary_type', models.CharField(max_length=50)),
                ('secondary_type', models.CharField(max_length=50)),
                ('sprite', models.CharField(max_length=200)),
            ],
        ),
    ]

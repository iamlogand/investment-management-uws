# Generated by Django 4.0.1 on 2022-01-19 17:47

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('portfolioapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolio',
            name='creation_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='portfolio',
            name='selected',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 2.2.4 on 2020-12-18 10:24

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_auto_20201218_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='access_duration',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

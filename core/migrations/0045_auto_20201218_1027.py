# Generated by Django 2.2.4 on 2020-12-18 10:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_auto_20201218_1024'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='access_duration',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='till',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

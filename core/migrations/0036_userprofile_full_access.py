# Generated by Django 2.2.4 on 2020-12-16 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_remove_userprofile_full_access'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='full_access',
            field=models.BooleanField(default=False),
        ),
    ]

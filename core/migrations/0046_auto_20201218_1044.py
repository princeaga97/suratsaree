# Generated by Django 2.2.4 on 2020-12-18 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0045_auto_20201218_1027'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='till',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='valid_till',
            field=models.DateField(null=True),
        ),
    ]

# Generated by Django 2.2.4 on 2020-12-18 10:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_auto_20201218_1017'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='stripe_customer_id',
            new_name='access_duration',
        ),
    ]

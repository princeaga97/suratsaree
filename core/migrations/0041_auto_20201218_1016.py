# Generated by Django 2.2.4 on 2020-12-18 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_auto_20201218_1015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='stripe_customer_id',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

# Generated by Django 2.2.4 on 2020-12-15 14:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_sharelist_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image_url',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.URLField()),
                ('item', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='image_url', to='core.Item')),
            ],
        ),
    ]

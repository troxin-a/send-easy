# Generated by Django 4.2.9 on 2024-08-21 11:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': {('block_user', 'Может блокировать пользователя')}},
        ),
    ]

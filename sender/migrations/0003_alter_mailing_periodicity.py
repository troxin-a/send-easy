# Generated by Django 5.0.7 on 2024-07-29 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0002_alter_client_options_alter_mailing_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailing',
            name='periodicity',
            field=models.CharField(choices=[('O', 'Одноразовая'), ('D', 'Раз в день'), ('W', 'Раз в неделю'), ('M', 'Раз в месяц')], default='O', help_text='Выберите периодичность запуска', max_length=1, verbose_name='Периодичность'),
        ),
    ]

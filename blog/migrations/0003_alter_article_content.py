# Generated by Django 4.2.9 on 2024-08-22 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_remove_article_image_article_preview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='content',
            field=models.TextField(blank=True, null=True, verbose_name='Содержимое статьи'),
        ),
    ]

# Generated by Django 5.0.1 on 2024-04-19 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0005_alter_hashtag_options_alter_post_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postfile',
            name='content',
            field=models.FileField(upload_to="[WindowsPath('E:/Programming/gitProjects/instagram-mock/backend/static')]users/posts/"),
        ),
    ]
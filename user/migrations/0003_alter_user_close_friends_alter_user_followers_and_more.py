# Generated by Django 5.0.1 on 2024-02-09 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_user_is_active_alter_user_nickname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='close_friends',
            field=models.ManyToManyField(blank=True, related_name='followings_close_friends', to='user.user'),
        ),
        migrations.AlterField(
            model_name='user',
            name='followers',
            field=models.ManyToManyField(blank=True, related_name='followings', through='user.Follows', to='user.user'),
        ),
        migrations.AlterField(
            model_name='user',
            name='hide_story',
            field=models.ManyToManyField(blank=True, related_name='followings_hide_story', to='user.user'),
        ),
    ]
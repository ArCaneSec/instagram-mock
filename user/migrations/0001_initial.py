# Generated by Django 5.0.1 on 2024-02-11 12:28

import django.db.models.deletion
import utils.auth_utils as utils
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Follows',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=250, unique=True)),
                ('nickname', models.CharField(blank=True, max_length=250)),
                ('first_name', models.CharField(max_length=250)),
                ('last_name', models.CharField(max_length=250)),
                ('profile', models.ImageField(blank=True, null=True, upload_to='static/users/profiles/')),
                ('biography', models.TextField(blank=True, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('phone_number', models.CharField(blank=True, max_length=11, null=True, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_private', models.BooleanField(default=False)),
                ('password', models.CharField(max_length=128)),
                ('salt', models.CharField(default=utils.generate_hash, max_length=100)),
                ('close_friends', models.ManyToManyField(blank=True, related_name='followings_close_friends', to='user.user')),
                ('followers', models.ManyToManyField(blank=True, related_name='followings', through='user.Follows', to='user.user')),
                ('hide_story', models.ManyToManyField(blank=True, related_name='followings_hide_story', to='user.user')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='follows',
            name='follower',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following_user', to='user.user'),
        ),
        migrations.AddField(
            model_name='follows',
            name='following',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followed_user', to='user.user'),
        ),
    ]

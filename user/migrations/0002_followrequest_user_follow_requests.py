# Generated by Django 5.0.1 on 2024-02-16 16:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FollowRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pending_follow_requests', to='user.user')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_follow_requets', to='user.user')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='follow_requests',
            field=models.ManyToManyField(blank=True, related_name='followings_follow_requests', through='user.FollowRequest', to='user.user'),
        ),
    ]

# Generated by Django 5.0.1 on 2024-02-17 11:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_follows_follower_alter_follows_following'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='followers',
        ),
    ]
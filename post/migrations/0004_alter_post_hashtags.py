# Generated by Django 5.0.1 on 2024-03-05 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0003_hashtag_post_hashtags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='hashtags',
            field=models.ManyToManyField(blank=True, related_name='posts', to='post.hashtag'),
        ),
    ]

# Generated by Django 5.0.1 on 2024-04-19 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_delete_lockedusername'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile',
            field=models.ImageField(blank=True, null=True, upload_to="[WindowsPath('E:/Programming/gitProjects/instagram-mock/backend/static')]users/profiles/"),
        ),
    ]

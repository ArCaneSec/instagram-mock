# Generated by Django 5.0.1 on 2024-04-19 16:57

import utils.model_utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('story', '0003_alter_story_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='content',
            field=models.FileField(upload_to=utils.model_utils.generate_path),
        ),
    ]
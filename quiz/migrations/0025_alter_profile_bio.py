# Generated by Django 4.0.1 on 2023-01-08 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0024_reportedquiz'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.TextField(default='Hi there! I like to quiz it up!'),
        ),
    ]

# Generated by Django 4.0.1 on 2023-01-15 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0026_reportedprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(default='/static/images/user_default.png', upload_to='users'),
        ),
    ]
# Generated by Django 4.0.1 on 2022-10-16 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0009_quizcomments_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizcomments',
            name='rating',
            field=models.IntegerField(default=0),
        ),
    ]

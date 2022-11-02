# Generated by Django 4.0.1 on 2022-08-24 11:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0006_quiz_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='userquizpoints',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='quiz',
            name='category',
            field=models.CharField(choices=[('0', 'History'), ('1', 'Geography'), ('2', 'Sports'), ('3', 'Entertainment'), ('4', 'Music'), ('5', 'Language'), ('6', 'Gaming'), ('7', 'Other')], max_length=20),
        ),
    ]
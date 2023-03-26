# Generated by Django 4.0.1 on 2023-01-26 16:10

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('quiz', '0033_rename_userquizpoints_user_quiz_points_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='QuizComment',
            new_name='Quiz_comment',
        ),
        migrations.RenameModel(
            old_name='ReportedComment',
            new_name='Reported_comment',
        ),
        migrations.RenameModel(
            old_name='ReportedProfile',
            new_name='Reported_profile',
        ),
        migrations.RenameModel(
            old_name='ReportedQuiz',
            new_name='Reported_quiz',
        ),
        migrations.RenameModel(
            old_name='UserCommentRelation',
            new_name='User_comment_relation',
        ),
    ]
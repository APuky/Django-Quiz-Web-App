from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


# Create your models here.

class Quiz(models.Model):
    choices = (
        ('history', "History"),
        ('geography', "Geography"),
        ('sports', "Sports"),
        ('entertainment', "Entertainment"),
        ('music', "Music"),
        ('language', "Language"),
        ('gaming', "Gaming"),
        ('other', "Other"),
    )

    title = models.CharField(max_length=40, unique=True, blank=False)
    description = models.CharField(max_length=100, blank=False)
    category = models.CharField(max_length=20, choices = choices)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Quizes"

class User_quiz_relation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    like = models.IntegerField(default=0)

class Question(models.Model):
    text = models.CharField(max_length=150, blank=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

class Choice(models.Model):
    choice = models.CharField(max_length=60, blank=False)
    is_right = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return self.choice

class User_quiz_points(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    points = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}, {self.quiz}"

    class Meta:
        verbose_name_plural = "User quiz points"

class Quiz_comment(models.Model):
    comment = models.CharField(max_length=160, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.comment

class User_comment_relation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Quiz_comment, on_delete=models.CASCADE)
    like = models.IntegerField(default=0)


class Reported_comment(models.Model):
    reportedby = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reportedby', default=1)
    user =  models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Quiz_comment, on_delete=models.CASCADE)
    reason = models.CharField(max_length=160, default='Reason')

    def __str__(self):
        return self.comment.comment

class Reported_quiz(models.Model):
    reportedbyuser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reportedbyuser', default=1)
    user =  models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    reason = models.CharField(max_length=160, default='Reason')

    def __str__(self):
        return self.quiz.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='users', default='default.png')
    bio = models.TextField(default='Hi there! I like to quiz it up!')

    def __str__(self):
        return self.user.username

class Reported_profile(models.Model):
    reportedbyuser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile_reported_by', default=1)
    user =  models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.CharField(max_length=160, default='Reason')
from django.contrib import admin
from .models import *

# Register your models here.



class ChoiceInline(admin.TabularInline):
    model = Choice

class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        ChoiceInline
    ]

class QuestionInline(admin.TabularInline):
    model = Question

class QuizAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'created_by')
    inlines = [
        QuestionInline
    ]

class CommentsAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'quiz', 'rating', 'created')
    list_filter = ('rating', 'created')

class ScoresAdmin(admin.ModelAdmin):
    readonly_fields = ('date',)

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(UserQuizPoints, ScoresAdmin)
admin.site.register(QuizComments, CommentsAdmin)

admin.site.register(Profile)

admin.site.site_url = '/home'




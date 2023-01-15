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
    readonly_fields = ('quiz', 'user')
    list_filter = ('rating', 'created')

class ScoresAdmin(admin.ModelAdmin):
    readonly_fields = ('date',)


class CommentReportsAdmin(admin.ModelAdmin):
    list_display =('comment', 'reason')
    readonly_fields = ('reportedby','user','comment','reason')

class QuizReportsAdmin(admin.ModelAdmin):
    list_display =('quiz','reason',)
    readonly_fields = ('reportedbyuser','user','reason', 'quiz')

class ProfileReportsAdmin(admin.ModelAdmin):
    list_display =('user','reason',)
    readonly_fields = ('reportedbyuser','user','reason')

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(UserQuizPoints, ScoresAdmin)
admin.site.register(QuizComments, CommentsAdmin)

admin.site.register(Profile)
admin.site.register(ReportedComments, CommentReportsAdmin)
admin.site.register(ReportedQuiz, QuizReportsAdmin)

admin.site.register(ReportedProfile, ProfileReportsAdmin)

admin.site.site_url = '/home'




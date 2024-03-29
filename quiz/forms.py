from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import *

from django.forms import formset_factory

class CreateNewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

        help_texts = {
            'username':'Minimum of 5 and Maximum of 20 Characters.'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'maxlength': 20, 'minlength': 5})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username')
    password = forms.CharField(max_length=150, widget=forms.PasswordInput, label='Password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder':'username'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder':'password'})


class CreateQuizForm(ModelForm):
    class Meta:
        model = Quiz
        fields = ['title','description','category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'maxlength':'40'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'maxlength':'100'})
        self.fields['category'].widget.attrs.update({'class': 'form-control'})



class QuestionsForm(forms.Form):
    Correct_Choice = (
        ("1", "Choice 1"),
        ("2", "Choice 2"),
        ("3", "Choice 3"),
        ("4", "Choice 4"),
    )
    Questiontext = forms.CharField(max_length=150, label='Question: *')
    choice1 = forms.CharField(max_length=60, label='Choice 1: *')
    choice2 = forms.CharField(max_length=60, label='Choice 2: *')
    choice3 = forms.CharField(max_length=60, label='Choice 3:', required=False)
    choice4 = forms.CharField(max_length=60, label='Choice 4:', required=False)
    correct_answer = forms.ChoiceField(choices = Correct_Choice, label='The correct answer: *')

    Questiontext.widget.attrs.update({'class':'form-control'})
    choice1.widget.attrs.update({'class':'form-control'})
    choice2.widget.attrs.update({'class':'form-control'})
    choice3.widget.attrs.update({'class':'form-control'})
    choice4.widget.attrs.update({'class':'form-control'})
    correct_answer.widget.attrs.update({'class':'form-control'})


class CommentForm(ModelForm):
    class Meta:
        model = Quiz_comment
        fields = ['comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs.update({'class': 'form-control'})


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bio'].widget.attrs.update({'class': 'form-control'})



class ProfileReportForm(ModelForm):
    class Meta:
        model = Reported_profile
        fields = ['reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].widget.attrs.update({'class': 'form-control'})

class ProfileAvatarForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].widget.attrs.update({'class': 'form-control'})

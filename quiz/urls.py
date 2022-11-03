from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.userRegister, name='register'),
    path('home/', views.homePage, name='home'),
    path('quiz/<str:pk>/', views.quizPage, name='quiz'),
    path('solve-quiz/<str:pk>/', views.solveQuizPage, name='solvequiz'),
    path('login/', views.userLogin, name='login'),
    path('logout/', views.userLogout, name='logout'),
    path('create-quiz/', views.createQuiz1, name='createquiz'),
    path('profile/<str:pk>/', views.userProfile, name='profile'),
    path('quiz/delete/<str:pk>/', views.deleteQuizPage, name='deletequizpage'),
    path('quiz/deleted/<str:pk>/', views.deleteQuiz, name='deletequiz'),
    path('quizes/<str:category>/', views.quizes, name='quizes'),
    path('quizes-search/', views.quizSearch, name='quizsearch')
]

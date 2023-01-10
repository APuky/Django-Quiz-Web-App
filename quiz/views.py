from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import *
from .models import *

from django.contrib import messages
from django.forms import formset_factory

from django.contrib.auth.decorators import login_required

from django.db.models import Count, Avg

from django.core.paginator import Paginator

from django.http import HttpResponseBadRequest, JsonResponse

import json

from django.forms.models import model_to_dict

def homePage(request):
	quiz = Quiz.objects.all()
	context = {'quiz': quiz}
	return render(request, 'quiz/home.html', context)



def quizPage(request,pk):
	quiz = Quiz.objects.get(id=pk)
	name = quiz.title
	users = UserQuizPoints.objects.filter(quiz__title=name).order_by('-date')[:10]
	solvedby = UserQuizPoints.objects.filter(quiz=pk).count()
	comments = QuizComments.objects.filter(quiz=pk).order_by('-created')

	paginator = Paginator(comments, 5)
	page_number = request.GET.get('page')
	page_comments = paginator.get_page(page_number)

	context = {'quiz': quiz, 'users': users, 'solvedby':solvedby, 'commentform':CommentForm, 'page_comments':page_comments}

	if request.user.is_authenticated:
		userattempts = UserQuizPoints.objects.filter(quiz__title=name).filter(user=request.user).order_by('date')[:5]
		userattemptstotal = UserQuizPoints.objects.filter(quiz__title=name).filter(user=request.user).count()
		context['userattempts'] = userattempts
		context['userattemptstotal'] = userattemptstotal


	is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
	print(request)
	if is_ajax:
		if request.method == 'POST':
			data = json.load(request)
			updated_values = data.get('payload')
			#ako ima commentid onda posalji kao comment report, ako ne onda je quiz report
			if 'commentid' in updated_values:
				comment = QuizComments.objects.get(id = int(updated_values['commentid']))
				user = comment.user

				report = ReportedComments(reportedby = request.user, user = user,comment = comment, reason = updated_values['reason'])
				report.save()
				return JsonResponse({'status': 'OK'}, status=200)
			else:
				report = ReportedQuiz(reportedbyuser = request.user, user = quiz.created_by, quiz = quiz, reason = updated_values['reason'])
				report.save()
				return JsonResponse({'status': 'OK'}, status=200)

		if request.method == 'GET':
			comments = list(QuizComments.objects.filter(quiz=quiz).values())
			#Model_to_dict je potreban zbog JSON
			return JsonResponse({'comments': comments, 'quiz':model_to_dict(quiz)})

		if request.method == 'PUT':
			data = json.load(request)
			updated_values = data.get('payload')
			like = updated_values['vote']
			#Check if this ajax request is for the comments or for the quiz
			if 'commentid' in updated_values:
				comment = comments.get(id=updated_values['commentid'])

				#Check if the user already upvoted/downvoted and block him from doing it again
				if not UserCommentRelation.objects.filter(user = request.user, comment = comment).exists():
					if like == 'like':
						comment.rating+=1
						usercomment = UserCommentRelation(user = request.user, comment = comment, like = 1)
						usercomment.save()
						comment.save()
					else:
						comment.rating-=1
						usercomment = UserCommentRelation(user = request.user, comment = comment, like = -1)
						usercomment.save()
						comment.save()
				else:
					currentcomment = UserCommentRelation.objects.get(user = request.user, comment = comment)
					if like == 'like':
						if currentcomment.like == 0:
							comment.rating += 1
							comment.save()
							currentcomment.like += 1
							currentcomment.save()
						elif currentcomment.like == -1:
							comment.rating +=2
							comment.save()
							currentcomment.like = 1
							currentcomment.save()
						else:
							comment.rating -= 1
							comment.save()
							currentcomment.like = 0
							currentcomment.save()

					if like == 'dislike':
						if currentcomment.like == 0:
							comment.rating -= 1
							comment.save()
							currentcomment.like = -1
							currentcomment.save()
						elif currentcomment.like == 1:
							comment.rating -= 2
							comment.save()
							currentcomment.like = -1
							currentcomment.save()
						else:
							comment.rating += 1
							comment.save()
							currentcomment.like = 0
							currentcomment.save()
			else:
				if not UserQuizRelation.objects.filter(user = request.user, quiz = quiz).exists():
					if like == 'like':
						quiz.rating+=1
						userquizrating = UserQuizRelation(user = request.user, quiz = quiz, like = 1)
						userquizrating.save()
						quiz.save()
					else:
						quiz.rating-=1
						userquizrating = UserQuizRelation(user = request.user, quiz = quiz, like = -1)
						userquizrating.save()
						quiz.save()
				else:
					userquizrating = UserQuizRelation.objects.get(user = request.user, quiz = quiz)
					if like == 'like':
						if userquizrating.like == 0:
							quiz.rating += 1
							quiz.save()
							userquizrating.like += 1
							userquizrating.save()
						elif userquizrating.like == -1:
							quiz.rating +=2
							quiz.save()
							userquizrating.like = 1
							userquizrating.save()
						else:
							quiz.rating -= 1
							quiz.save()
							userquizrating.like = 0
							userquizrating.save()

					if like == 'dislike':
						if userquizrating.like == 0:
							quiz.rating -= 1
							quiz.save()
							userquizrating.like = -1
							userquizrating.save()
						elif userquizrating.like == 1:
							quiz.rating -= 2
							quiz.save()
							userquizrating.like = -1
							userquizrating.save()
						else:
							quiz.rating += 1
							quiz.save()
							userquizrating.like = 0
							userquizrating.save()

			
			return JsonResponse({'status': 'OK'}, status=200)
			
		return JsonResponse({'status': 'Invalid request'}, status=400)
	else:
		if request.method == 'POST':
			form = CommentForm(request.POST)
			if form.is_valid():
				comment = form.save(commit=False)
				comment.user = request.user
				comment.quiz = quiz
				comment.save()
				return redirect('quiz', pk=quiz.id)
	

	return render(request, 'quiz/quiz.html', context)


def userRegister(request):
	form = CreateNewUserForm()

	if request.method == 'POST':
		form = CreateNewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			messages.info(request, "Account successfuly created! Please login with your credentials.")
			return redirect("login")
	context = {'form':form}
	return render(request, 'quiz/registration.html', context)


def userLogin(request):
	if request.method == "POST":
		data=request.POST
		form = AuthenticationForm(request, data)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("home")
			else:
				messages.error(request,"This user does not exist.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request, "quiz/login.html", context={"login_form":form})

def userLogout(request):
	logout(request)
	return redirect('home')


@login_required
def createQuiz(request):
	questionFormset = formset_factory(QuizCreateForm, extra=20)
	if request.method == 'POST':
		quiznewform=CreateQuizForm(request.POST)
		quizformset=questionFormset(request.POST)

		if quiznewform.is_valid():
			#formData = quizform.cleaned_data
			obj = quiznewform.save(commit=False)
			obj.created_by = request.user

			#CHECK IF THE USER PUT IN THE CHOICE THAT HE SELECTED AS CORRECT
			for form in quizformset:
				if form.is_valid():
					print("Checking")
					data = form.cleaned_data
					answer = data.get('correct_answer')
					question = Question(text=data.get('Questiontext'), quiz=obj)

					for i in range(1,5):
						if i == int(answer):
							choice = Choice(choice=data.get(f'choice{i}'), is_right=True, question=question)
							if choice.choice.strip()=='':
								messages.add_message(request, messages.ERROR, f'You marked an answer as correct but did not provide one!')
								context={'quizformset':quizformset, 'quiznewform':quiznewform}
								return render(request, 'quiz/createquiz.html', context)
							
			obj.save()

			for form in quizformset:
				if form.is_valid():
					data = form.cleaned_data
					answer = data.get('correct_answer')
					
					question = Question(text=data.get('Questiontext'), quiz=obj)
					question.save()

					for i in range(1,5):
						if i == int(answer):
							choice = Choice(choice=data.get(f'choice{i}'), is_right=True, question=question)
							if choice.choice.strip() != '':
								choice.save()
						else:
							choice = Choice(choice=data.get(f'choice{i}'), is_right=False, question=question)
							if choice.choice.strip() != '':
								choice.save()
			
		else:
			for error in quiznewform.errors:
				if error == 'title':
					messages.add_message(request, messages.ERROR, f'A quiz already exists with the same title!')
				else:
					messages.add_message(request, messages.ERROR, f'Unexpected error, make sure all the required fields are filled.')
			context = {'quizformset':quizformset, 'quiznewform':quiznewform}
			return render(request, 'quiz/createquiz.html', context)	
			
		return redirect('quiz', pk=obj.id)

	
	else:
		quiznewform=CreateQuizForm()
		quizformset=questionFormset()


	context = {'quizformset':quizformset, 'quiznewform':quiznewform}
	return render(request, 'quiz/createquiz.html', context)


def deleteQuizPage(request, pk):
	quiz=Quiz.objects.get(id=pk)
	if request.user == quiz.created_by:
		return render(request, 'quiz/deletequiz.html', context={'quiz':quiz})
	else:
		#return redirect('quiz', pk=quiz.id)
		return redirect('https://www.youtube.com/watch?v=Tf3uK2RGU2c')
	print(quiz.created_by)
	
def deleteQuiz(request,pk):
	quiz=Quiz.objects.get(id=pk)
	if request.user == quiz.created_by:
		quiz.delete()
		messages.add_message(request, messages.SUCCESS, 'You successfully deleted your quiz!')
		return redirect('home')
	else:
		#return redirect('quiz', pk=quiz.id)
		return redirect('https://www.youtube.com/watch?v=Tf3uK2RGU2c')

def solveQuizPage(request, pk):

	
	if request.method == 'POST':
		#print(request.POST)
		choices = Choice.objects.filter(question__quiz_id=pk)
		
		quiz = Quiz.objects.get(id=pk)
		questions = Question.objects.filter(quiz=pk)


		#print(questions)
		score=0
		
		for pair in request.POST.items():
			if pair[0].isnumeric() and pair[1].isnumeric():
				question = Question.objects.get(id=int(pair[0]))
				if question.quiz == quiz:
					correct_answer=choices.filter(question=question).get(is_right=True)
					if int(pair[1]) == correct_answer.id:
						score += 1

		if request.user.is_authenticated:
			userscore = UserQuizPoints(user=request.user, quiz=quiz, points=score)
			userscore.save()
		messages.add_message(request, messages.SUCCESS, f'You scored {score}/{questions.count()} points!')

		return redirect('quiz', pk=pk)

	else:
		pass
	
	quiz = Quiz.objects.get(id=pk)
	name = quiz.title
	questions = Question.objects.filter(quiz=pk)
	choices = Choice.objects.filter(question__quiz_id=pk)
	question_number=questions.first().id - 1
	for question in questions:
		question.number = question.id - question_number
	context = {'quiz': quiz, 'questions':questions, 'choices':choices, 'form1':QuizSolveForm, 'number':question_number}
	return render(request, 'quiz/solve_quiz.html', context)


@login_required
def userProfile(request, pk):

	scores = UserQuizPoints.objects.filter(user=pk).order_by('-date')
	profile = Profile.objects.get(user_id=pk)

	paginator = Paginator(scores, 5)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	#If you are accessing your own stats page
	if request.user.id == int(pk):
		form = ProfileForm(instance=request.user.profile)

		if request.method == 'POST':
			form = ProfileForm(request.POST, instance=request.user.profile)

			if form.is_valid():
				form.save()
				messages.add_message(request, messages.SUCCESS, f'Profile successfully updated!')
				profile = Profile.objects.get(user_id=pk)
		form = ProfileForm(instance=request.user.profile)
		context = {'scores':scores, 'form':form, 'stats':profile, 'searchdata':page_obj}
		return render(request, 'quiz/profile.html', context)

	context = {'scores':scores, 'stats':profile, 'searchdata':page_obj}
	return render(request, 'quiz/profile.html', context)

def quizes(request, category):
	popular=Quiz.objects.annotate(count=Count('userquizpoints')).order_by('-count').filter(category=category)
	context={'quizes':popular, 'search':'Popular'}
	
	if request.method == 'POST':
		sort_by=request.POST['sort']
		print(request.POST['sort'])
		if sort_by == 'popular':
			popular=Quiz.objects.annotate(count=Count('userquizpoints')).order_by('-count').filter(category=category)
			context={'quizes':popular, 'search':'Popular'}
		elif sort_by == 'newest':
			newest=Quiz.objects.filter(category=category).order_by('-created').annotate(count=Count('userquizpoints'))
			context={'quizes':newest, 'search':'Newest'}
		elif sort_by == 'oldest':
			oldest=Quiz.objects.filter(category=category).order_by('created').annotate(count=Count('userquizpoints'))
			context={'quizes':oldest, 'search':'Oldest'}
		elif sort_by == 'easiest':
			easiest=Quiz.objects.filter(category=category).annotate(rate=Avg('userquizpoints__points')).order_by('-rating').annotate(count=Count('userquizpoints'))
			context={'quizes':easiest, 'search':'Easiest'}
		#Django paginator je salje GET request svaki put kada se stranica promijeni, što znači da se onda queryset defaulta na popularne kvizove svaki put.
		#Ovaj ispod kod iz get requesta izvlači "search" i po tome onda slaže queryset
		#"search" je dodan u urlu, pogledaj u templateu u navigaciji kod paginacije
		#https://stackoverflow.com/questions/150505/capturing-url-parameters-in-request-get
		#MOGUĆE POBOLJŠAT
	
	if request.method == 'GET':

		if request.GET.get('search') == 'Newest':
			newest=Quiz.objects.filter(category=category).order_by('-created').annotate(count=Count('userquizpoints'))
			context={'quizes':newest, 'search':'Newest'}
			
		elif request.GET.get('search') == 'Oldest':
			oldest=Quiz.objects.filter(category=category).order_by('created').annotate(count=Count('userquizpoints'))
			context={'quizes':oldest, 'search':'Oldest'}

		elif request.GET.get('search') == 'Easiest':
			easiest=Quiz.objects.filter(category=category).annotate(rate=Avg('userquizpoints__points')).order_by('-rating').annotate(count=Count('userquizpoints'))
			context={'quizes':easiest, 'search':'Easiest'}
	
	
	paginator = Paginator(context['quizes'],5)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	context['searchdata']=page_obj

	return render(request, 'quiz/quizes.html', context)

def quizSearch(request):
	search=(request.GET.get("search"))
	quizes=Quiz.objects.annotate(count=Count('userquizpoints')).order_by('-count').filter(title__icontains=search)
	context={'quizes':quizes, 'sort':'Popular'}
	
	if request.method == 'POST':
		sort_by=request.POST['sort']
		if sort_by == 'popular':
			popular=Quiz.objects.annotate(count=Count('userquizpoints')).order_by('-count').filter(title__icontains=search)
			context={'quizes':popular, 'sort':'Popular'}
		elif sort_by == 'newest':
			newest=Quiz.objects.filter(title__icontains=search).order_by('-created').annotate(count=Count('userquizpoints'))
			context={'quizes':newest, 'sort':'Newest'}
		elif sort_by == 'oldest':
			oldest=Quiz.objects.filter(title__icontains=search).order_by('created').annotate(count=Count('userquizpoints'))
			context={'quizes':oldest, 'sort':'Oldest'}
		elif sort_by == 'easiest':
			easiest=Quiz.objects.filter(title__icontains=search).annotate(rate=Avg('userquizpoints__points')).order_by('-rating').annotate(count=Count('userquizpoints'))
			context={'quizes':easiest, 'sort':'Easiest'}
   # Ovo ima veze sa URLovima u html templateu, iz urla čitam te podatke
	if request.method == 'GET':
		if request.GET.get('sort') == 'Newest':
			newest=Quiz.objects.filter(title__icontains=search).order_by('-created').annotate(count=Count('userquizpoints'))
			context={'quizes':newest, 'sort':'Newest'}
			
		elif request.GET.get('sort') == 'Oldest':
			oldest=Quiz.objects.filter(title__icontains=search).order_by('created').annotate(count=Count('userquizpoints'))
			context={'quizes':oldest, 'sort':'Oldest'}
			
		elif request.GET.get('sort') == 'Easiest':
			easiest=Quiz.objects.filter(title__icontains=search).annotate(rate=Avg('userquizpoints__points')).order_by('-rating').annotate(count=Count('userquizpoints'))
			context={'quizes':easiest, 'sort':'Easiest'}

	paginator = Paginator(context['quizes'], 5)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)

	context['searchdata']=page_obj
	context['query']=search
	return render(request, 'quiz/quizes_search.html', context)
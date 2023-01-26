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


from .functions import *

def homePage(request):
	popular_quizes = Quiz.objects.all().annotate(count=Count('user_quiz_points')).order_by('-count')[:5]
	newest_quizes = Quiz.objects.all().order_by('-created')[:5]
	best_rated_quizes = Quiz.objects.all().annotate(rate=Avg('user_quiz_points__points')).order_by('-rating')[:5]
	context = {'popular': popular_quizes, 'newest':newest_quizes, 'best':best_rated_quizes}
	return render(request, 'quiz/home.html', context)



def quizPage(request,pk):
	quiz = Quiz.objects.get(id=pk)
	name = quiz.title
	users = User_quiz_points.objects.filter(quiz__title=name).order_by('-date')[:10]
	solvedby = User_quiz_points.objects.filter(quiz=pk).count()
	comments = Quiz_comment.objects.filter(quiz=pk).order_by('-created')

	##Add the avatar image of the user to the comments queryset
	for comment in comments:
		data = Profile.objects.get(user=comment.user)
		comment.avatar = data.avatar

	paginator = Paginator(comments, 5)
	page_number = request.GET.get('page')
	page_comments = paginator.get_page(page_number)

	context = {'quiz': quiz, 'users': users, 'solvedby':solvedby, 'commentform':CommentForm, 'page_comments':page_comments}

	if request.user.is_authenticated:
		if User_quiz_points.objects.filter(quiz__title=name).filter(user=request.user).exists():
			userattempts = User_quiz_points.objects.filter(quiz__title=name).filter(user=request.user).order_by('-date')[:5]
			userattemptstotal = User_quiz_points.objects.filter(quiz__title=name).filter(user=request.user).count()
			bestattempt=User_quiz_points.objects.filter(quiz__title=name).filter(user=request.user).order_by('-points')[0]
			context['userattempts'] = userattempts
			context['userattemptstotal'] = userattemptstotal
			context['bestattempt'] = bestattempt


	is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
	print(request)
	if is_ajax:
		if request.method == 'POST':
			data = json.load(request)
			updated_values = data.get('payload')
			#ako ima commentid onda posalji kao comment report, ako ne onda je quiz report
			if 'commentid' in updated_values:
				comment = Quiz_comment.objects.get(id = int(updated_values['commentid']))
				user = comment.user
				report = Reported_comment(reportedby = request.user, user = user,comment = comment, reason = updated_values['reason'])
				report.save()
				return JsonResponse({'status': 'OK'}, status=200)
				
			else:
				report = Reported_quiz(reportedbyuser = request.user, user = quiz.created_by, quiz = quiz, reason = updated_values['reason'])
				report.save()
				return JsonResponse({'status': 'OK'}, status=200)

		if request.method == 'GET':
			comments = list(Quiz_comment.objects.filter(quiz=quiz).values())
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
				if not User_comment_relation.objects.filter(user = request.user, comment = comment).exists():
					if like == 'like':
						comment.rating+=1
						usercomment = User_comment_relation(user = request.user, comment = comment, like = 1)
						usercomment.save()
						comment.save()
					else:
						comment.rating-=1
						usercomment = User_comment_relation(user = request.user, comment = comment, like = -1)
						usercomment.save()
						comment.save()
				else:
					currentcomment = User_comment_relation.objects.get(user = request.user, comment = comment)
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
				if not User_quiz_relation.objects.filter(user = request.user, quiz = quiz).exists():
					if like == 'like':
						quiz.rating+=1
						userquizrating = User_quiz_relation(user = request.user, quiz = quiz, like = 1)
						userquizrating.save()
						quiz.save()
					else:
						quiz.rating-=1
						userquizrating = User_quiz_relation(user = request.user, quiz = quiz, like = -1)
						userquizrating.save()
						quiz.save()
				else:
					userquizrating = User_quiz_relation.objects.get(user = request.user, quiz = quiz)
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
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("home")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = LoginForm()
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
		return redirect('quiz', pk=quiz.id)
	
def deleteQuiz(request,pk):
	quiz=Quiz.objects.get(id=pk)
	if request.user == quiz.created_by:
		quiz.delete()
		messages.add_message(request, messages.SUCCESS, 'Quiz successfully deleted.')
		return redirect('home')
	else:
		return redirect('quiz', pk=quiz.id)


def solveQuizPage(request, pk):

	
	if request.method == 'POST':
		#print(request.POST)
		choices = Choice.objects.filter(question__quiz_id=pk)
		
		quiz = Quiz.objects.get(id=pk)
		questions = Question.objects.filter(quiz=pk)


		#print(questions)
		score=0
		
		for pair in request.POST.items():
			#pair[0] je question id, pair[1] je choice id
			if pair[0].isnumeric() and pair[1].isnumeric():
				question = Question.objects.get(id=int(pair[0]))
				if question.quiz == quiz:
					correct_answer=choices.filter(question=question).get(is_right=True)
					#ako je id pair[1] jednak id točnog odgovora na to pitanje
					if int(pair[1]) == correct_answer.id:
						score += 1

		if request.user.is_authenticated:
			userscore = User_quiz_points(user=request.user, quiz=quiz, points=score)
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
def userProfile(request, username):
	user_id = User.objects.get(username = username)
	profile = Profile.objects.get(user=user_id)
	scores = User_quiz_points.objects.filter(user=user_id).order_by('-date')
	created_quizes = Quiz.objects.filter(created_by=user_id).order_by('-created')

	paginator = Paginator(scores, 5)
	page_number = request.GET.get('page1')
	page_obj1 = paginator.get_page(page_number)

	paginator = Paginator(created_quizes, 5)
	page_number = request.GET.get('page2')
	page_obj2 = paginator.get_page(page_number)


	#### For average scores in profile
	############
	categories = {
		'history': 0,
		'geography':0,
		'sports':0,
		'entertainment':0,
		'music':0,
		'language':0,
		'gaming':0,
		'other':0,
	}
	amount_solved = {}
	for cat in categories:
		categories[cat] = get_average(cat, scores, Question)
		amount_solved[cat] = get_amount_of_solved(cat, scores, Quiz)

    ###################
	#If you are accessing your own stats page
	if request.user.username == username:
		image_form = ProfileAvatarForm()
		form = ProfileForm(instance=request.user.profile)

		if request.method == 'POST':
			if 'bio' in request.POST:
				form = ProfileForm(request.POST, instance=request.user.profile)

				if form.is_valid():
					form.save()
					profile = Profile.objects.get(user=user_id)
			else:
				form = ProfileAvatarForm(request.POST, request.FILES)
				if form.is_valid():
					## Form is filled with the user instance / It only updates the avatar field, without it it would either try to create a new instance or you would have a unique constraint
					update = ProfileAvatarForm(request.POST, request.FILES, instance = profile)
					update.save()


		context = {'scores':scores, 'form_update':form, 'avatar_form':image_form, 'stats':profile, 'searchdata':page_obj1, 'createdquizes':page_obj2, 'cat_scores':categories, 'amount_solved':amount_solved}
		return render(request, 'quiz/profile.html', context)

	else:
		if request.method == 'POST':
			if 'reason' in request.POST:
				form = ProfileReportForm(request.POST)
				if form.is_valid():
					report = form.save(commit=False)
					report.reportedbyuser = request.user
					report.user = user_id
					report.save()
		else:
			form = ProfileReportForm()



		context = {'scores':scores, 'form':form, 'stats':profile, 'searchdata':page_obj1, 'createdquizes':page_obj2, 'cat_scores':categories, 'amount_solved':amount_solved}
		return render(request, 'quiz/profile.html', context)

	context = {'scores':scores, 'stats':profile, 'form':form, 'searchdata':page_obj1, 'createdquizes':page_obj2, 'cat_scores':categories, 'amount_solved':amount_solved}
	return render(request, 'quiz/profile.html', context)



def quizes(request, category):
	popular=Quiz.objects.annotate(count=Count('user_quiz_points')).order_by('-count').filter(category=category)
	context={'quizes':popular, 'search':'Popular'}
	
	if request.method == 'POST':
		sort_by=request.POST['sort']
		print(request.POST['sort'])
		if sort_by == 'popular':
			popular=Quiz.objects.annotate(count=Count('user_quiz_points')).order_by('-count').filter(category=category)
			context={'quizes':popular, 'search':'Popular'}
		elif sort_by == 'newest':
			newest=Quiz.objects.filter(category=category).order_by('-created').annotate(count=Count('user_quiz_points'))
			context={'quizes':newest, 'search':'Newest'}
		elif sort_by == 'oldest':
			oldest=Quiz.objects.filter(category=category).order_by('created').annotate(count=Count('user_quiz_points'))
			context={'quizes':oldest, 'search':'Oldest'}
		elif sort_by == 'rating':
			rating=Quiz.objects.filter(category=category).annotate(rate=Avg('user_quiz_points__points')).order_by('-rating').annotate(count=Count('user_quiz_points'))
			context={'quizes':rating, 'search':'Best Rated'}
		#Django paginator je salje GET request svaki put kada se stranica promijeni, što znači da se onda queryset defaulta na popularne kvizove svaki put.
		#Ovaj ispod kod iz get requesta izvlači "search" i po tome onda slaže queryset
		#"search" je dodan u urlu, pogledaj u templateu u navigaciji kod paginacije
		#https://stackoverflow.com/questions/150505/capturing-url-parameters-in-request-get
		#MOGUĆE POBOLJŠAT
	
	if request.method == 'GET':

		if request.GET.get('search') == 'Newest':
			newest=Quiz.objects.filter(category=category).order_by('-created').annotate(count=Count('user_quiz_points'))
			context={'quizes':newest, 'search':'Newest'}
			
		elif request.GET.get('search') == 'Oldest':
			oldest=Quiz.objects.filter(category=category).order_by('created').annotate(count=Count('user_quiz_points'))
			context={'quizes':oldest, 'search':'Oldest'}

		elif request.GET.get('search') == 'Best Rated':
			rating=Quiz.objects.filter(category=category).annotate(rate=Avg('user_quiz_points__points')).order_by('-rating').annotate(count=Count('user_quiz_points'))
			context={'quizes':rating, 'search':'Best Rated'}
	
	
	paginator = Paginator(context['quizes'],5)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	context['searchdata']=page_obj

	return render(request, 'quiz/quizes.html', context)

def quizSearch(request):
	search=(request.GET.get("search"))
	if search == None :
		search = ''
	quizes=Quiz.objects.annotate(count=Count('user_quiz_points')).order_by('-count').filter(title__icontains=search)
	context={'quizes':quizes, 'sort':'Popular'}
	
	if request.method == 'POST':
		sort_by=request.POST['sort']
		if sort_by == 'popular':
			popular=Quiz.objects.annotate(count=Count('user_quiz_points')).order_by('-count').filter(title__icontains=search)
			context={'quizes':popular, 'sort':'Popular'}
		elif sort_by == 'newest':
			newest=Quiz.objects.filter(title__icontains=search).order_by('-created').annotate(count=Count('user_quiz_points'))
			context={'quizes':newest, 'sort':'Newest'}
		elif sort_by == 'oldest':
			oldest=Quiz.objects.filter(title__icontains=search).order_by('created').annotate(count=Count('user_quiz_points'))
			context={'quizes':oldest, 'sort':'Oldest'}
		elif sort_by == 'rating':
			rating=Quiz.objects.filter(title__icontains=search).annotate(rate=Avg('user_quiz_points__points')).order_by('-rating').annotate(count=Count('user_quiz_points'))
			context={'quizes':rating, 'sort':'Best Rated'}
   # Ovo ima veze sa URLovima u html templateu, iz urla čitam te podatke
	if request.method == 'GET':
		if request.GET.get('sort') == 'Newest':
			newest=Quiz.objects.filter(title__icontains=search).order_by('-created').annotate(count=Count('user_quiz_points'))
			context={'quizes':newest, 'sort':'Newest'}
			
		elif request.GET.get('sort') == 'Oldest':
			oldest=Quiz.objects.filter(title__icontains=search).order_by('created').annotate(count=Count('user_quiz_points'))
			context={'quizes':oldest, 'sort':'Oldest'}
			
		elif request.GET.get('sort') == 'Best Rated':
			rating=Quiz.objects.filter(title__icontains=search).annotate(rate=Avg('user_quiz_points__points')).order_by('-rating').annotate(count=Count('user_quiz_points'))
			context={'quizes':rating, 'sort':'Best Rated'}

	paginator = Paginator(context['quizes'], 5)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)

	context['searchdata']=page_obj
	context['query']=search
	return render(request, 'quiz/quizes_search.html', context)
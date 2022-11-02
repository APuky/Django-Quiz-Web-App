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

def homePage(request):
	quiz = Quiz.objects.all()
	context = {'quiz': quiz}
	return render(request, 'quiz/home.html', context)



def quizPage(request,pk):
	quiz = Quiz.objects.get(id=pk)
	name = quiz.title
	users = UserQuizPoints.objects.filter(quiz__title=name).order_by('-points')[:10]
	solvedby = UserQuizPoints.objects.filter(quiz=pk).count()
	comments = QuizComments.objects.filter(quiz=pk).order_by('-created')

	paginator = Paginator(comments, 5)
	page_number = request.GET.get('page')
	page_comments = paginator.get_page(page_number)

	context = {'quiz': quiz, 'users': users, 'solvedby':solvedby, 'commentform':CommentForm, 'page_comments':page_comments}

	is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

	if is_ajax:
		if request.method == 'GET':
			comments = list(QuizComments.objects.all().values())
			return JsonResponse({'context': comments})

		if request.method == 'PUT':
			data = json.load(request)
			updated_values = data.get('payload')
			comment=comments.get(id=updated_values['commentid'])
			like = updated_values['vote']

			#Check if the user already upvoted/downvoted and block him from doing it again
			if not UserCommentRelation.objects.filter(user = request.user, comment = comment).exists():
				if like == 'like':
					comment.rating+=1
					usercomment = UserCommentRelation(user = request.user, comment = comment, like = True)
					usercomment.save()
					comment.save()
				else:
					comment.rating-=1
					usercomment = UserCommentRelation(user = request.user, comment = comment, like = False)
					usercomment.save()
					comment.save()
			else:
				currentcomment = UserCommentRelation.objects.get(user = request.user, comment = comment)
				if currentcomment.like:
					if like == 'like':
						pass
					else:
						comment.rating-=1
						comment.save()
						currentcomment.like=False
						currentcomment.save()
				else:
					if like == 'like':
						comment.rating+=1
						comment.save()
						currentcomment.like=True
						currentcomment.save()


				
			
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
	questionFormset = formset_factory(QuizCreateForm, extra=2)
	if request.method == 'POST':
		quiznewform=CreateQuizForm(request.POST)

		quizformset=questionFormset(request.POST)

		if quizformset.is_valid():
			#formData = quizform.cleaned_data
			print("works here1")
			obj = quiznewform.save(commit=False)
			obj.created_by = request.user
			obj.save()

			print("works here1")


			for form in quizformset:
				data = form.cleaned_data
				answer = data.get('correct_answer')
				
				question = Question(text=data.get('Questiontext'), quiz=Quiz.objects.latest('created'))
				question.save()

				for i in range(1,5):
					if i == int(answer):
						choice = Choice(choice=data.get(f'choice{i}'), is_right=True, question=Question.objects.order_by('-pk')[0])
						choice.save()
					else:
						choice = Choice(choice=data.get(f'choice{i}'), is_right=False, question=Question.objects.order_by('-pk')[0])
						choice.save()

			
			return redirect('home')
	
	else:
		quiznewform=CreateQuizForm()
		quizformset=questionFormset()


	context = {'quizformset':quizformset, 'quiznewform':quiznewform}
	return render(request, 'quiz/createquiz.html', context)

@login_required
def createQuiz1(request):
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
			print(quizformset.non_form_errors())
			print(quizformset.errors)
			print("Error")
			context = {'quizformset':quizformset, 'quiznewform':quiznewform}
			return render(request, 'quiz/createquiz.html', context)	
			
		return redirect('home')

	
	else:
		quiznewform=CreateQuizForm()
		quizformset=questionFormset()


	context = {'quizformset':quizformset, 'quiznewform':quiznewform}
	return render(request, 'quiz/createquiz.html', context)

@login_required
def createQuiz2(request):
	questionFormset = formset_factory(QuizCreateForm, extra=20)
	if request.method == 'POST':
		quiznewform=CreateQuizForm(request.POST)
		quizformset=questionFormset(request.POST)

		if quiznewform.is_valid():
			#formData = quizform.cleaned_data
			obj = quiznewform.save(commit=False)
			obj.created_by = request.user
			obj.save()

			for form in quizformset:
				if form.is_valid():
					print("Is valid.")
					if form.cleaned_data.get("Questiontext")!='':
						if form.cleaned_data.get("choice1")!='' and form.cleaned_data.get("choice2")!='' and form.cleaned_data.get("choice3")!='' and form.cleaned_data.get("choice4")!='':
							print(form.cleaned_data.get("Questiontext"))
							print(type(form.cleaned_data.get("Questiontext")))
							data = form.cleaned_data
							answer = data.get('correct_answer')
							
							question = Question(text=data.get('Questiontext'), quiz=Quiz.objects.latest('created'))
							question.save()

							for i in range(1,5):
								if i == int(answer):
									choice = Choice(choice=data.get(f'choice{i}'), is_right=True, question=Question.objects.order_by('-pk')[0])
									choice.save()
								else:
									choice = Choice(choice=data.get(f'choice{i}'), is_right=False, question=Question.objects.order_by('-pk')[0])
									choice.save()
										

				else:
					break
			
			return redirect('home')

	
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
		print(request.POST)
		choices = Choice.objects.filter(question__quiz_id=pk)
		
		quiz = Quiz.objects.get(id=pk)
		questions = Question.objects.filter(quiz=pk)


		print(questions)
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
	print(choices)
	context = {'quiz': quiz, 'questions':questions, 'choices':choices, 'form1':QuizSolveForm}
	return render(request, 'quiz/solve_quiz.html', context)


def solveQuizPageBackup(request, pk):
	
	if request.method == 'POST':
		print(request.POST)
		answers = request.POST.getlist('answer')
		choices = Choice.objects.filter(question__quiz_id=pk)
		
		quiz = Quiz.objects.get(id=pk)
		questions = Question.objects.filter(quiz=pk)
		
		score=0
		for num, question in enumerate(questions):
			set_choice=question.choice_set.all()
			for number, choice in enumerate(set_choice):
				if choice.is_right == True:
					if int(answers[num]) == number:
						score+=1		
				else:
					pass
		if request.user.is_authenticated:
			userscore= UserQuizPoints(user=request.user, quiz=quiz, points=score)
			userscore.save()
		messages.add_message(request, messages.SUCCESS, f'You scored {score}/{questions.count()} points!')
		print(score)
		print(pk)
		print(request.user.id)

		return redirect('quiz', pk=pk)

	else:
		pass
	
	quiz = Quiz.objects.get(id=pk)
	name = quiz.title
	questions = Question.objects.filter(quiz=pk)
	choices = Choice.objects.filter(question__quiz_id=pk)
	print(choices)
	context = {'quiz': quiz, 'questions':questions, 'choices':choices, 'form1':QuizSolveForm}
	return render(request, 'quiz/solve_quiz.html', context)

@login_required
def userProfile(request, pk):

	scores = UserQuizPoints.objects.filter(user=pk).order_by('-date')
	profile = Profile.objects.get(user_id=pk)
	#If you are accessing your own stats page
	if request.user.id == int(pk):
		form = ProfileForm(instance=request.user.profile)
		context = {'scores':scores, 'form':form}

		if request.method == 'POST':
			form = ProfileForm(request.POST, instance=request.user.profile)

			if form.is_valid():
				form.save()
				messages.add_message(request, messages.SUCCESS, f'Profile successfully updated!')
		form = ProfileForm(instance=request.user.profile)
		context = {'scores':scores, 'form':form}
		return render(request, 'quiz/profile.html', context)

	context = {'scores':scores, 'stats':profile}
	return render(request, 'quiz/profile.html', context)


def quizes(request, pk):
	quizesPopular=Quiz.objects.annotate(count=Count('userquizpoints')).order_by('-count').filter(category=pk)[:10]
	quizesNewest=Quiz.objects.filter(category=pk).order_by('-created')[:10]
	quizesEasiest=Quiz.objects.filter(category=pk).annotate(rating=Avg('userquizpoints__points')).order_by('-rating')
	for quiz in quizesEasiest:
		print(quiz)
	context={'quizesPopular':quizesPopular, 'quizesNewest':quizesNewest, 'quizesEasiest':quizesEasiest}
	return render(request, 'quiz/quizes.html', context)

def quizSearch(request):
	search=(request.GET.get("search"))
	quizes=Quiz.objects.filter(title__icontains=search)
	paginator = Paginator(quizes, 6)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	context={'searchdata':page_obj, 'query':search}
	return render(request, 'quiz/home.html', context)
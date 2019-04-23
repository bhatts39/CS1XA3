from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.template.loader import get_template
from django.contrib.auth import *
from django.contrib.auth.models import User
from trivia.models import *
import requests, time, json, random

def login_view(request):
    if request.method == "POST":
        t = get_template('login.html')
        html = t.render()
        return HttpResponse(html)
    elif request.method == "GET":
        username = request.GET['username']
        password = request.GET['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse("success")
        else:
            return HttpResponse("fail")

def home_view(request):
    if(request.user.is_authenticated):
        return HttpResponse("logged in")
    else:
        return HttpResponse("not logged in")
        
def logout_view(request):
    logout(request)
    return HttpResponse("logged out")

def register_view(request):
    if request.method == "POST":
        t = get_template('lsogin.html')
        html = t.render()
        return HttpResponse(html)
    elif request.method == "GET":
        username = request.GET['username']
        password = request.GET['password']
        email = request.GET['email']
        user = User.objects.create_user(username, email, password)
        user.info.score = 0
        user.save()
        return HttpResponse("success")
        
def findgame_view(request):
    if(request.user.is_authenticated):
        game = Game.objects.filter((Q(status=0) | Q(status=1)) & Q(p1=request.user) | Q(p2=request.user)).first()
        if game is not None:
            return JsonResponse({'error':'already in a game'})
        game = Game.objects.filter(status=0).first()
        if game == None:
            question = newTriviaQuestion()
            game = Game(status=0,p1=request.user,question=question)
            game.save()
            return JsonResponse({'status':'0','gameid':game.id})
        else:
            game.p2 = request.user
            game.status = 1
            game.save()
            return JsonResponse({'status':'1','gameid':game.id})
            

def gameinfo_view(request):
    if request.method == "GET" and request.user.is_authenticated:
        game = Game.objects.filter(Q(id=request.GET['gameid']) & Q(p1=request.user) | Q(p2=request.user)).first()
        if game is not None:
            player = 'p1' if game.p1 == request.user else 'p2'
            p2 = '' if game.p2 == None else game.p2.id
            return JsonResponse({'status':game.status,
                                'player':player,
                                'p1':game.p1.id,
                                'p2':p2,
                                'p1choice':game.p1choice,
                                'p2choice':game.p2choice,
                                'question':game.question.id,
                                'questionNum':game.questionNum}) 
        else:
            return JsonResponse({'error':'game not found'})
def newTriviaQuestion():
    response = requests.get("https://opentdb.com/api.php?amount=1&difficulty=medium&type=multiple")
    data = json.loads(response.text).get('results')[0]
    question = data.get('question')
    correctChoice = random.randint(0,3)
    answers = data.get('incorrect_answers')
    answers.insert(correctChoice,data.get('correct_answer'))
    q = TriviaQuestion(question=question,
                        category=data.get('category'),
                        choice1=answers[0],
                        choice2=answers[1],
                        choice3=answers[2],
                        choice4=answers[3],
                        correctChoice=correctChoice)
    q.save() 
    return q
        

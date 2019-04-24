from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.forms.models import model_to_dict
from django.template.loader import get_template
from django.contrib.auth import *
from django.contrib.auth.models import User
from trivia.models import *
from django.core.serializers import serialize
from django.core.exceptions import ObjectDoesNotExist
import requests, time, json, random


def home_view(request):
    if(request.user.is_authenticated):
        return render(request,'home.html',{'user':request.user})
    else:
        return redirect('login')

def login_view(request):
     return render(request,'login.html')

def register_view(request):
    return render(request,'register.html')

def login_api_view(request):
    username = request.GET['username']
    password = request.GET['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponse("success")
    else:
        return HttpResponse("fail")
        
def logout_api_view(request):
    logout(request)
    return HttpResponse("logged out")

def register_api_view(request):
    username = request.GET['username']
    password = request.GET['password']
    email = request.GET['email']
    user = User.objects.create_user(username, email, password)
    user.info.score = 0
    user.save()
    return HttpResponse("success")
        
def findgame_view(request):
    if(request.user.is_authenticated):
        game = Game.objects.filter((Q(status=0) | Q(status=1)) & Q(p1__user=request.user) | Q(p2__user=request.user)).first()
        if game is not None:
            return JsonResponse({'error':'already in a game'})
        game = Game.objects.filter(status=0).first()
        if game == None:
            question = newTriviaQuestion()
            p1 = Player(user=request.user)
            p1.save()
            game = Game(status=0,p1=p1,question=question,questionTime=int(time.time()*1000))
            game.save()
            p1.game = game
            p1.save()
            return JsonResponse({'status':'0',
                                'gameid':game.id,
                                'question':game.question.id,
                                'playerid':game.p1.id})
        else:
            p2 = Player(user=request.user,game=game)
            p2.save()
            game.p2 = p2
            game.status = 1 
            game.questionTime = int(time.time()*1000)
            game.save()
            return JsonResponse({'status':'1',
                                'gameid':game.id,
                                'question':game.question.id,
                                'playerid':game.p2.id})
            
def gameinfo_view(request):
    if request.method == "GET" and request.user.is_authenticated:
        player = Game.objects.filter(id=request.GET['pid'],user=request.user).first()
        if player is not None:
            game = player.game
            question = model_to_dict(game.question)
            question.pop('correctChoice')
            return JsonResponse({'status':game.status,
                                'question':game.question,
                                'questionNum':game.questionNum,
                                'questionTime':game.questionTime}) 
        else: 
            return JsonResponse({'error':'game not found'})

def getquestion_view(request):
    if request.method == "GET" and request.user.is_authenticated:
        try:
            triviaQ = TriviaQuestion.objects.get(id=request.GET['qid'])
            return JsonResponse(model_to_dict(triviaQ))
        except ObjectDoesNotExist:
            return JsonResponse({'error':'question not found'})

#long polling
def wait_view(request):
    if request.method == "GET" and request.user.is_authenticated:
        playerid = int(request.GET['pid'])

        try:
            player = Player.objects.get(id=playerid)
        except ObjectDoesNotExist:
            return JsonResponse({'error':'player not found'})

        if player.game.status != 1:
            return HttpResponse("error")

        opponent = player.game.p1 if player == player.game.p2 else player.game.p2
        correctAnswer = player.game.question.correctChoice

        while(True):
            player.refresh_from_db()
            opponent.refresh_from_db()
            if player.choice == correctAnswer:
                result = JsonResponse({'result':'usercorrect','opponentAnswer':opponent.choice})
                if(player.game.status == 1):
                    nextQuestion(player.game)
                return result
            if opponent.choice == correctAnswer:
                return JsonResponse({'result':'opponentcorrect','opponentAnswer':opponent.choice})
            if player.choice is not None and opponent.choice is not None:
                    result = JsonResponse({'result':'bothincorrect','correctAnswer':correctAnswer})
                    if player.game.p1 == player:
                        nextQuestion(player.game)
                    return result
            time.sleep(0.3)
                


def selectanswer_view(request):
    if request.method == "GET" and request.user.is_authenticated:
        playerid = int(request.GET['playerid'])
        questionid = int(request.GET['questionid'])
        choice = int(request.GET['choice'])

        try:
            player = Player.objects.get(id=playerid)
        except ObjectDoesNotExist:
            return JsonResponse({'error':'player not found'})

        opponent = player.game.p1 if player == player.game.p2 else player.game.p2

        #user doesn't match player
        if player.user != request.user:
            return JsonResponse({'error':'access denied'})

        #other opponent answered correct first (rare conflict)
        if player.game.question.id != int(questionid):
            return JsonResponse({'result':'not submitted'})

        if player.choice is not None:
            return JsonResponse({'result':'error already selected choice'})
        player.choice = choice
        player.save()
        #player chose incorrect answer
        if player.choice != player.game.question.correctChoice:
            return JsonResponse({'result':'incorrect'})

        #player chose correct anwer
        player.score += 1
        #game over
        if(player.score > 6):
            player.game.winner = player
            player.game.status = 2
            winner = 'true'
        else:
            winner = 'false'

        player.save()

        return JsonResponse({'result':'correct','winner':winner})
        
        

def nextQuestion(game):
    game.question = newTriviaQuestion()
    game.questionTime = int(time.time()*1000)
    game.questionNum += 1
    game.p1.choice = None
    game.p2.choice = None
    game.save()

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
                        correctChoice=correctChoice+1)
    q.save() 
    return q
        

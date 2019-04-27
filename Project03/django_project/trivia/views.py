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
from django.views.decorators.csrf import csrf_exempt


def home_view(request):
    if(request.user.is_authenticated):
        topusers = User.objects.order_by('-username')[:10]
        return render(request,'home.html',{'user':request.user,'topusers':topusers})
    else:
        return redirect('login')

def login_view(request):
    if(not request.user.is_authenticated):
        return render(request,'login.html')
    else:
        return redirect('../')

def register_view(request):
    if(not request.user.is_authenticated):
        return render(request,'register.html')
    else:
        return redirect('../')

def logout_view(request):
    logout(request)
    return redirect('../')

def matchmaking_view(request):
    if(request.user.is_authenticated):
        return render(request,'matchmaking.html')
    else:
        return redirect('../')

def game_view(request):
    if(request.user.is_authenticated):
        try:
            player = Player.objects.get(id=int(request.GET['pid']))
        except ObjectDoesNotExist:
            return JsonResponse({'error':'player not found'})

        if player.user != request.user:
            return HttpResponse("{'error':'wrong game'}")

        return render(request,'game.html',{'playerid':player.id})
    else:
        return redirect('login')       

@csrf_exempt
def login_api_view(request):
    if(not request.user.is_authenticated):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'result':'success'})
        else:
            return JsonResponse({'result':'fail'})

@csrf_exempt
def register_api_view(request):
    if(not request.user.is_authenticated):
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        try:
            user = User.objects.create_user(username, email, password)
        except:
            return JsonResponse({'result':'fail'})
        user.info.score = 0
        user.save()
        login(request, user)
        return JsonResponse({'result':'success'})

@csrf_exempt
def findgame_view(request):
    if(request.user.is_authenticated):
        game = Game.objects.filter((Q(status=0) | Q(status=1)) & (Q(p1__user=request.user) | Q(p2__user=request.user))).first()
        if game is not None:
            pid = game.p1.id if game.p1.user == request.user else game.p2.id
            return JsonResponse({'status':game.status,'playerid':pid})
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

@csrf_exempt
def cancelgame_view(request):
    if(request.user.is_authenticated):
        playerid = int(request.POST['playerid'])
        player = Player.objects.filter(id=playerid).first()
        if player == None or player.game.status != 0:
            return JsonResponse({'result':'error'})
        player.game.status=2
        player.save()
        return JsonResponse({'result':'cancelled'})

@csrf_exempt            
def gameinfo_view(request):
    if request.method == "POST" and request.user.is_authenticated:
        player = Player.objects.filter(id=request.POST['pid'],user=request.user).first()
        if player is not None:
            game = player.game
            opponent = game.p2 if game.p1 == player else game.p1
            if opponent == None:
                return JsonResponse({'status':game.status})
            question = model_to_dict(game.question)
            question.pop('correctChoice')
            return JsonResponse({'status':game.status,
                                'question':question,
                                'opponentName':opponent.user.username,
                                'opponentPoints':opponent.score,
                                'playerPoints':player.score,
                                'questionNum':game.questionNum,
                                'questionTime':game.questionTime}) 
        else: 
            return JsonResponse({'error':'game not found'})
@csrf_exempt
def getquestion_view(request):
    if request.method == "GET" and request.user.is_authenticated:
        try:
            triviaQ = TriviaQuestion.objects.get(id=request.GET['qid'])
            return JsonResponse(model_to_dict(triviaQ))
        except ObjectDoesNotExist:
            return JsonResponse({'error':'question not found'})

#todo opponentcorrect not showing up sometimes for p2
#add sounds
@csrf_exempt
def wait_view(request):
     if request.method == "POST" and request.user.is_authenticated:
        playerid = int(request.POST['pid'])

        try:
            player = Player.objects.get(id=playerid)
        except ObjectDoesNotExist:
            return JsonResponse({'result':'error'})

        if player.game.status < 1:
            return JsonResponse({'result':'error'})
        
        opponent = player.game.p1 if player == player.game.p2 else player.game.p2
        questionNum = player.game.questionNum

        while(True):
            player.refresh_from_db()
            opponent.refresh_from_db()

            if (player.next and opponent.next) or (player.game.questionNum > questionNum):
                player.next = False
                if player == player.game.p1:
                    player.choice = None
                    opponent.choice = None
                    player.save()
                    opponent.save()
                    nextQuestion(player.game)
                    time.sleep(1)
                return JsonResponse({'result':'nextquestion'})

            if player.choice == player.game.question.correctChoice:
                player.next = True
                player.save()
                return JsonResponse({'result':'usercorrect','opponentAnswer':opponent.choice,'status':player.game.status})
            elif opponent.choice == player.game.question.correctChoice:
                player.next = True
                player.save()
                return JsonResponse({'result':'opponentcorrect','opponentAnswer':opponent.choice,'status':player.game.status})
            elif player.choice is not None and opponent.choice is not None:
                player.next = True
                player.save()
                return JsonResponse({'result':'bothincorrect','opponentAnswer':opponent.choice,'status':player.game.status})
            time.sleep(0.2)
    

@csrf_exempt
def selectanswer_view(request):
    if request.method == "POST" and request.user.is_authenticated:
        playerid = int(request.POST['playerid'])
        questionid = int(request.POST['questionid'])
        choice = int(request.POST['choice'])

        try:
            player = Player.objects.get(id=playerid)
        except ObjectDoesNotExist:
            return JsonResponse({'result':'error'})

        opponent = player.game.p1 if player == player.game.p2 else player.game.p2

        #user doesn't match player
        if player.user != request.user:
            return JsonResponse({'result':'error wrong user'})

        #other opponent answered correct first (rare conflict)
        if opponent.choice == player.game.question.correctChoice:
            return JsonResponse({'result':'error wrong question'})

        if player.choice is not None:
            return JsonResponse({'result':'error already selected'})
        player.choice = choice
        player.save()

        #player chose incorrect answer
        if player.choice != player.game.question.correctChoice:
            return JsonResponse({'result':'incorrect','correctAnswer':player.game.question.correctChoice})

        #player chose correct anwer
        player.score += 1
        #game over
        if(player.score > 4):
            player.game.winner = player
            player.game.status = 2
            player.user.points += 1
            player.game.save()
            winner = 'true'
        else:
            winner = 'false'

        player.save()

        return JsonResponse({'result':'correct','winner':winner})
        
        

def nextQuestion(game):
    game.p1.choice = None
    game.p2.choice = None
    game.question = newTriviaQuestion()
    game.questionTime = int(time.time()*1000)
    game.questionNum += 1
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
        

from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth import *
from django.contrib.auth.models import User

def login_view(request):
    if request.method == "POST":
        t = get_template('login.html')
        html = t.render()
        return HttpResponse(html)
    elif request.method == "GET":
        username = request.GET['username']
        password = request.GET['password']
        user = authenticate(requzest, username=username, password=password)
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
        t = get_template('login.html')
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
        
def register_view(request):
    if request.method == "POST":
        t = get_template('login.html')
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
        
        

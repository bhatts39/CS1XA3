from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def checkPass(request):
	username = request.POST.get("user","")
	password = request.POST.get("pass","")
	if(username == "Jimmy") and (password == "Hendrix"):
		return HttpResponse("Cool")
	else:
		return HttpResponse("Bad User Name")

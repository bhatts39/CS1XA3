from django.shortcuts import render
from django.http import HttpResponse

def hello_world(request):
     html = "<html><body>Hello World</body></html>"
     return HttpResponse(html)

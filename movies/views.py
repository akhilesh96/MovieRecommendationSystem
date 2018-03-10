from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

def index(request):
    if not request.user.is_authenticated:
        return render(request, 'movies/login.html')
    else:
        return render(request, 'movies/home.html')

def home(request):
    return render(request,'movies/home.html')

def signup(request):
    return render(request,'movies/signup.html')
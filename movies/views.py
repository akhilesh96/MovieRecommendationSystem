from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import UserProfile
import sys

from .forms import UserForm,GenreForm,NewForm
def index(request):
        return render(request, 'movies/base.html')


def home(request):
    print(request.user)
    return render(request,'movies/home.html')




def login_user(request):
    if request.method == "POST":
        foo = request.POST['user_field']
        password = request.POST['pass_field']
        qs=User.objects.all()
        for i in qs:
            if i.username== foo or i.email==foo:
                user=authenticate(username=i.username,password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return render(request, 'movies/home.html')
            else:
                return render(request, 'movies/base.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'movies/base.html', {'error_message': 'Invalid login'})
    return render(request, 'movies/base.html')



def signup(request):
    if request.method == "POST":
        user_reg=request.POST['username_reg']
        password_reg=request.POST['pass_reg']
        email_reg=request.POST['email_reg']
        qset=User.objects.all()
        for i in qset:
            if i.email == email_reg:
                print('inside error')
                error=True
                return render(request, 'movies/base.html', {'error': error})
        u= User(username=user_reg,email=email_reg)
        u.set_password(password_reg)
        u.save()
        user = authenticate(username=user_reg, password=password_reg)
        if user is not None:
            if user.is_active:
                login(request, user)
                genreform = GenreForm()
                return render(request, 'movies/interests.html', {'genreform': genreform})

    return render(request, 'movies/base.html')


def reg_home(request):
    if request.method =="POST":
        form = GenreForm(request.POST or None)
        if form.is_valid():
            checked_vals = request.POST.getlist('genres')

            UserProfile.objects.filter(user_id=request.user.id).update(genres=checked_vals)

            return render(request, 'movies/home.html')





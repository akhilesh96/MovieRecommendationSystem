from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.models import User
import sys

from .forms import UserForm,GenreForm,NewForm
def index(request):
    if not request.user.is_authenticated:
        return render(request, 'movies/base.html')
    else:
        return render(request, 'movies/home.html')

def home(request):
    return render(request,'movies/home.html')

# def home(request):
#
#     form=GenreForm(request.POST)
#     if form.is_valid():
#         genreform=form.save(commit=False)
#         genres=genreform.clea
#
#
#
#     return render(request,'movies/home.html')

# def signup(request):
#     form = UserForm(request.POST or None)
#     if form.is_valid():
#         user = form.save(commit=False)
#         username = form.cleaned_data['username']
#         password = form.cleaned_data['password']
#         user.set_password(password)
#         user.save()
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             if user.is_active:
#
#                 genreform = GenreForm()
#                 newform= NewForm()
#                 return render(request, 'movies/interests.html',{'newform' :newform})
#     context = {
#         "form": form,
#     }
#     return render(request, 'movies/register.html', context)
#




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
                return render(request, 'movies/base.html', {'error_message': 'Email already exist'})
        u= User(username=user_reg,email=email_reg)
        u.set_password(password_reg)
        u.save()
        print("saved user")
        user = authenticate(username=user_reg, password=password_reg)
        if user is not None:
            if user.is_active:
                genreform = GenreForm()
                return render(request, 'movies/interests.html', {'genreform': genreform})

    return render(request, 'movies/base.html')



from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import UserProfile
from imdbpie import Imdb
from django.http import HttpResponseRedirect
import sys
import csv
from itertools import islice
import operator


from .forms import UserForm,GenreForm,NewForm



import os
import heapq

import numpy as np
import pandas as pd
import wsgiref
from collections import Counter
from operator import itemgetter
from django.utils.encoding import smart_str
from django.http import HttpResponse

##########################################################################
## Module Constants
##########################################################################

BASE  = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
PATH  = os.path.join(BASE, "data", "C:\\Users\\Akhilesh\\Downloads\\ml-latest\\new.csv")
PRIOR = [2, 2, 2, 2, 2]

##########################################################################
## Analysis Object
##########################################################################

class Ratings(object):
    @property
    def movies(self):
        """
        Returns the data grouped by Movie
        """
        k=self.data.groupby(["title","genres","movieId"])
        return k
    def get_means(self):
        return self.movies['rating'].mean()

    def get_counts(self):
        return self.movies['rating'].count()

    def load(self):
        self.data = pd.read_csv(self.path)
    def __init__(self, path=PATH, m=None, C=None):
        self.path  = path
        self.prior = m
        self.confidence = C
        self.load()

    def bayesian_mean(self, arr):
        if not self.prior or not self.confidence:
            raise TypeError("Bayesian mean must be computed with m and C")

        return ((self.confidence * self.prior + arr.sum()) /
                (self.confidence + arr.count()))

    ...

    def get_bayesian_estimates(self):
        return self.movies['rating'].agg(self.bayesian_mean)

    def top_movies(self, n=10):
        grid   = pd.DataFrame({
                    'mean':  self.get_means(),
                    'count': self.get_counts(),
                    'bayes': self.get_bayesian_estimates()
                 })

        return grid.ix[grid['bayes'].argsort()[-n:]]



def retreive(UserRequest):
    movieId = []
    movieTitle = []
    movieDictionary = {}
    genreDictionary={}
    genre = []
    UserGenres = []
    open_file = open('C:\\Users\\Akhilesh\\Downloads\\ml-latest\\links.csv', encoding="utf8")
    reader = csv.reader(open_file)
    next(reader, None)
    w, h = 18, 1;
    Matrix = [[0 for x in range(h)] for y in range(w)]
    usr = UserProfile.objects.filter(user=UserRequest)
    gen=usr.values_list('genres')
    ls=gen[0]
    for i in ls[0]:
        i=int(i)
        Matrix[i-1][0]=1

    ratings = Ratings(m=3.5, C=50)
    genrerecommend={}

    topratedmovies=ratings.top_movies(n=100)
    for r in topratedmovies.iterrows():
        moviegenres=r[0][1].split('|')
        count=0
        for i in moviegenres:
            if i!=" " and i!="":
                k=int(i)
                if Matrix[k-1][0]:
                    count=count+1
        genrerecommend[r[0][0],r[0][2]]=count
    sorted_genres = sorted(genrerecommend.items(), key=operator.itemgetter(1),reverse=True)
    movie_id=[]
    imdb_id=[]
    movies_list=[]
    for i in sorted_genres[:6]:
        movie_id.append(i[0][1])
        movies_list.append(i[0][0])
    for j in movie_id:
        j=str(j)
        for row in reader:
            if j == row[0]:
                imdb_id.append(row[1])
        open_file.seek(0)
        reader = csv.reader(open_file)
    imdb = Imdb()
    genre_top=[]
    d=[]
    for i in range(0,6):
        items = imdb.get_title_videos('tt'+imdb_id[i])
        d.append(items['image']['url'])

    return (d,movies_list)
def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))
def index(request):
        return render(request, 'movies/base.html')

def moviedata():
    imdb = Imdb()
    pop_items = imdb.get_popular_movies()
    dict = pop_items['ranks']
    d = []
    r = []
    moviedetails = []
    n_list = []
    for i in range(0, 6):
        d.append(dict[i]['image']['url'])
        r.append(dict[i]['title'])
        r.append(dict[i]['year'])
        movie_id = dict[i]['id']
        ls = movie_id.split('/')
        # rating = imdb.get_title_ratings(ls[2])
        try:
            # r.append(rating['rating'])
            r.append(0)
        except:
            r.append(0)

        n_list.append(d)
        moviedetails.append(r)
        d = []
        r = []
    return (n_list,moviedetails)

def home(request):

    n_list, moviedetails = moviedata()

    k1,k2=retreive(request.user)
    return render(request, 'movies/home.html', {'dict': n_list, 'moviedetails': moviedetails,'k1':k1,'k2':k2})
    return render(request, 'movies/home.html')

def login_user(request):
    if request.method == "POST":
        foo = request.POST['user_field']
        password = request.POST['pass_field']
        qs=User.objects.all()
        if foo=='' or password=='':
            return render(request, 'movies/base.html', {'error_message': 'Username or Password is Empty'})

        for i in qs:
            if i.username== foo or i.email==foo:
                user=authenticate(username=i.username,password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/home')
            else:
                return render(request, 'movies/base.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'movies/base.html', {'error_message': 'Invalid login'})
    return render(request, 'movies/base.html')

def logout_user(request):
    logout(request)
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
            n_list, moviedetails = moviedata()
            return render(request, 'movies/home.html', {'dict': n_list, 'moviedetails': moviedetails})





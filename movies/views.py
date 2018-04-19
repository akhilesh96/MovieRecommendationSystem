from __future__ import division
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
import simplejson as json
from django.http import HttpResponse
from haystack.query import SearchQuerySet

from .forms import UserForm, GenreForm, NewForm

import re

from django.db.models import Q

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

BASE = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
PATH = os.path.join(BASE, "data", "C:\\Users\\Akhilesh\\Downloads\\ml-latest\\new.csv")
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
        k = self.data.groupby(["title", "genres", "movieId"])
        return k

    def get_means(self):
        return self.movies['rating'].mean()

    def get_counts(self):
        return self.movies['rating'].count()

    def load(self):
        self.data = pd.read_csv(self.path)

    def __init__(self, path=PATH, m=None, C=None):
        self.path = path
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
        grid = pd.DataFrame({
            'mean': self.get_means(),
            'count': self.get_counts(),
            'bayes': self.get_bayesian_estimates()
        })

        return grid.ix[grid['bayes'].argsort()[-n:]]


def retreive(UserRequest):
    movieId = []
    movieTitle = []
    movieDictionary = {}
    genreDictionary = {}
    genre = []
    UserGenres = []
    open_file = open('C:\\Users\\Akhilesh\\Downloads\\ml-latest\\links.csv', encoding="utf8")
    reader = csv.reader(open_file)
    next(reader, None)
    w, h = 18, 1;
    Matrix = [[0 for x in range(h)] for y in range(w)]
    usr = UserProfile.objects.filter(user=UserRequest)
    gen = usr.values_list('genres')
    ls = gen[0]
    for i in ls[0]:
        i = int(i)
        Matrix[i - 1][0] = 1

    ratings = Ratings(m=3.5, C=50)
    genrerecommend = {}

    topratedmovies = ratings.top_movies(n=150)
    topratedmovies = topratedmovies.sort_values(by='bayes', ascending=False)

    for r in topratedmovies.iterrows():
        moviegenres = r[0][1].split('|')
        count = 0
        for i in moviegenres:
            if i != " " and i != "":
                k = int(i)
                if Matrix[k - 1][0]:
                    count = count + 1
        bayesscore = round(r[1][0], 3)
        genrerecommend[r[0][0], r[0][2], bayesscore] = count * bayesscore

    sorted_genres = sorted(genrerecommend.items(), key=operator.itemgetter(1), reverse=True)

    movie_id = []
    imdb_id = []
    movies_list = {}
    # movies_list=[]
    d = []
    for i in sorted_genres[:6]:
        movie_id.append(i[0][1])
        movies_list[i[0][0], i[0][1]] = i[0][2]
        # d.append(i[0][0])
        # d.append(i[0][2])

        # movies_list.append(d)
        # d=[]

        #   print(movie_id)
    # print(movies_list)
    movies_list = sorted(movies_list.items(), key=operator.itemgetter(1), reverse=True)

    for j in range(0, 6):
        j = str(movies_list[j][0][1])
        for row in reader:
            if j == row[0]:
                imdb_id.append(row[1])
                # print(imdb_id)
        open_file.seek(0)
        reader = csv.reader(open_file)
    imdb = Imdb()

    genre_top = []
    d = []
    for i in range(0, 6):
        items = imdb.get_title('tt' + imdb_id[i])
        d.append(items['base']['image']['url'])

    # print(d)
    # print(movies_list)
    movies_list1 = {}
    for j in range(0, 6):
        tile = movies_list[j][0][0]
        movies_list1[tile] = movies_list[j][1]
    movies_list1 = sorted(movies_list1.items(), key=operator.itemgetter(1), reverse=True)
    print(movies_list1)
    return (d, movies_list1)


def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))


def index(request):
    return render(request, 'movies/base.html')


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def search(request):
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

        entry_query = get_query(query_string, ['title', 'body', ])

        found_entries = Entry.objects.filter(entry_query).order_by('-pub_date')

    return render('search/search_results.html',
                  {'query_string': query_string, 'found_entries': found_entries})


def search(request):
    query = request.GET.get('q')
    open_file = open('C:\\Users\\Akhilesh\\Downloads\\ml-latest\\movies.csv', encoding="utf8")
    reader = csv.reader(open_file)
    next(reader, None)
    for row in reader:
        if query.lower() in row[1].lower():
            print(row)


#
# def search(request):
#     sqs = SearchQuerySet().autocomplete(content_auto=request.GET.get('q', ''))[:5]
#     suggestions = [result.title for result in sqs]
#     # Make sure you return a JSON object, not a bare list.
#     # Otherwise, you could be vulnerable to an XSS attack.
#     the_data = json.dumps({
#         'results': suggestions
#     })
#     return HttpResponse(the_data, content_type='application/json')
def detail(request, movie_id):
    if not request.user.is_authenticated():
        return render(request, 'movies/base.html')
    else:
        user = request.user
        imdb = Imdb()
        titledetails = imdb.get_title(movie_id)
        dlist = []
        try:
            dlist.append(titledetails['base']['image']['url'])
        except:
            # insert a null image
            dlist.append(' ')

        dlist.append(titledetails['base']['title'])
        dlist.append(titledetails['base']['year'])
        try:
            dlist.append(titledetails['base']['runningTimeInMinutes'])
        except:
            dlist.append('-')

        dlist.append(imdb.get_title_genres(movie_id)['genres'])
        try:
            dlist.append(titledetails['plot']['summaries'][0]['text'])
        except:
            dlist.append('-')
        try:
            print('hei')
            castandcrew = imdb.get_title_credits(movie_id)
            castlist = []
            detdict={}
            detdict['director']=castandcrew['credits']['director'][0]['name']
            detdict['producer']=castandcrew['credits']['producer'][0]['name']
            writers = []
            for i in castandcrew['credits']['writer']:
                writers.append(i['name'])
            detdict['writers']=writers
            dlist.append(detdict)
            for i in range(0, 5):
                castdict = {}
                castdict[castandcrew['credits']['cast'][i]['name']] = castandcrew['credits']['cast'][i]['characters']
                castlist.append(castdict)
            dlist.append(castlist)
        except:
            dlist.append('-')
        return render(request, 'movies/moviedetails.html', {'dlist': dlist})


def moviedata():
    imdb = Imdb()
    pop_items = imdb.get_popular_movies()
    dict = pop_items['ranks']
    d = []
    r = []
    moviedetails = []
    n_list = []
    for i in range(0, 6):
        tempdict = {}
        movie_id = dict[i]['id']
        ls = movie_id.split('/')
        rating = imdb.get_title_ratings(ls[2])
        url = dict[i]['image']['url']
        tempdict[ls[2]] = dict[i]['title']
        d.append(tempdict)
        d.append(url)
        r.append(dict[i]['title'])
        t = str(dict[i]['year'])
        r.append("(" + t + ")")

        # rg=int(rating['rating']) / 2

        try:
            rg = rating['rating'] / 2
            r.append(rg)
        # print(rating['rating'])
        except:
            r.append(0)

        n_list.append(d)
        # print(r)
        moviedetails.append(r)
        d = []
        r = []
    return (n_list, moviedetails)


def home(request):
    n_list, moviedetails = moviedata()

    k1, k2 = retreive(request.user)
    return render(request, 'movies/home.html', {'dict': n_list, 'moviedetails': moviedetails, 'k1': k1, 'k2': k2})
    return render(request, 'movies/home.html')


def login_user(request):
    if request.method == "POST":
        foo = request.POST['user_field']
        password = request.POST['pass_field']
        qs = User.objects.all()
        if foo == '' or password == '':
            return render(request, 'movies/base.html', {'error_message': 'Username or Password is Empty'})

        for i in qs:
            if i.username == foo or i.email == foo:
                user = authenticate(username=i.username, password=password)
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
        user_reg = request.POST['username_reg']
        password_reg = request.POST['pass_reg']
        email_reg = request.POST['email_reg']
        qset = User.objects.all()
        for i in qset:
            if i.email == email_reg:
                print('inside error')
                error = True
                return render(request, 'movies/base.html', {'error': error})
        u = User(username=user_reg, email=email_reg)
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
    if request.method == "POST":
        form = GenreForm(request.POST or None)
        if form.is_valid():
            checked_vals = request.POST.getlist('genres')
            UserProfile.objects.filter(user_id=request.user.id).update(genres=checked_vals)
            # n_list, moviedetails = moviedata()
            return redirect('/home')
        else:
            genreform = GenreForm()

            return render(request, 'movies/interests.html',
                          {'genreform': genreform, 'error_message': 'Select atleast one genre'})


            # return render(request, 'movies/home.html', {'dict': n_list, 'moviedetails': moviedetails})

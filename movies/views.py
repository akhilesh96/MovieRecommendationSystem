from __future__ import division
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import UserProfiles
from imdbpie import Imdb
from django.http import HttpResponseRedirect
import sys
import csv,math
import time
from itertools import islice
import operator
import simplejson as json
from django.http import HttpResponse
from haystack.query import SearchQuerySet

from .forms import UserForm, GenreForm, NewForm
from django.views.decorators.csrf import csrf_exempt

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

def loadMovieLens(path='C:\\Users\\Akhilesh\\Downloads\\ml-latest'):
    # Get movie titles
    movies={}
    # with open(path+'\\movies.csv', encoding='UTF8') as f:
    #     next(f)
    #     for line in f:
    #         (id1,title)=line.split(',')[0:2]
    #         movies[id1]=title
    # Load data
    prefs={}
    with open(path+'\\ratings.csv', encoding='UTF8') as f:
        next(f)
        for line in f:
            (user,movieid,rating,ts)=line.split(',')
            prefs.setdefault(user,{})
            prefs[user][movieid]=float(rating)
    return prefs

def sim_pearson(prefs,p1,p2):
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item]=1
    n=len(si)
    if n==0: return 0
    sum1=sum([prefs[p1][it] for it in si])
    sum2=sum([prefs[p2][it] for it in si])
    sum1Sq=sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq=sum([pow(prefs[p2][it],2) for it in si])
    pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])
    num=pSum-(sum1*sum2/n)
    den=math.sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    if den==0: return 0
    r=num/den
    return r

def getRecommendations(prefs,person,similarity=sim_pearson):
    totals = {}
    simSums = {}
    for other in prefs:
        if other == person:
            continue
        sim = similarity(prefs,person,other)
        if sim<=0:
           continue
        for item in prefs[other]:
            if item not in prefs[person] or prefs[person][item]==0:
                totals.setdefault(item,0)
                totals[item]+=prefs[other][item]*sim
                simSums.setdefault(item,0)
                simSums[item]+=sim
    rankings=[(total/simSums[item],item) for item,total in totals.items( )]
    rankings.sort( )
    rankings.reverse( )
    return rankings

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
    usr = UserProfiles.objects.filter(user=UserRequest)
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
    #print(sorted_genres)
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
    #print(movies_list)
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
    # print(d)
    # print(movies_list)

    newlist=[]
    d=[]
    images_file = open('C:\\Users\\Akhilesh\\Downloads\\ml-latest\\imagesnew.csv', encoding="utf8")
    reader = csv.reader(images_file)
    next(reader, None)
    for j in range(0, 6):
        movlist=[]
        m1=[]
        movies_list1 = {}
        d1={}
       # items = imdb.get_title('tt' + imdb_id[j])
        tile = movies_list[j][0][0]
        for k in reader:
            if imdb_id[j]==k[1]:
                m1.append(k[2])
                movieid=k[0]
                # d.append(k[2])
                break
        movies_list1[movieid] = movies_list[j][1]
        images_file.seek(0)
        reader = csv.reader(images_file)
        d1['tt'+imdb_id[j]]=tile
        m1.append(d1)
        movlist.append(tile)
        movlist.append(movies_list1)
        newlist.append(movlist)
        d.append(m1)

    # movies_list1 = sorted(movies_list1.items(), key=operator.itemgetter(1), reverse=True)
    return (d,newlist)


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
        detlist=[]
        try:
            dlist.append(titledetails['base']['image']['url'])
        except:
            # insert a null image
            dlist.append(' ')

        detlist.append(titledetails['base']['title'])
        title=titledetails['base']['title']
        detlist.append(titledetails['base']['year'])
        try:
            min=int(titledetails['base']['runningTimeInMinutes'])
            hrs=int(min/60)
            minutes=min-60*hrs
            time=str(hrs)+'hr '+str(minutes)+'min'

            detlist.append(time)
        except:
            detlist.append('-')

        detlist.append(imdb.get_title_genres(movie_id)['genres'])
        try:
            detlist.append(titledetails['plot']['summaries'][0]['text'])
        except:
            detlist.append('-')
        try:
            #print('hello')
            castandcrew = imdb.get_title_credits(movie_id)
            castlist = []
            detdict={}
            detdict['director']=castandcrew['credits']['director'][0]['name']
            detdict['producer']=castandcrew['credits']['producer'][0]['name']
            writers = []
            for i in castandcrew['credits']['writer']:
                writers.append(i['name'])
            writerset=set(writers)
            detdict['writers']=list(writerset)

            detlist.append(detdict)
            for i in range(0, 6):
                castdict = {}
                castdict[castandcrew['credits']['cast'][i]['name']] = castandcrew['credits']['cast'][i]['characters']
                castlist.append(castdict)
            detlist.append(castlist)
        except:
            detlist.append('-')
        dlist.append(detlist)
        return render(request, 'movies/moviedetails.html', {'dlist': dlist,'title':title})


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
        t = str(dict[i]['year'])
        r.append(dict[i]['title']+("(" + t + ")"))

       # r.append("(" + t + ")")

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
    #print(n_list)
    return (n_list, moviedetails)


def home(request):
    n_list, moviedetails = moviedata()
    # preferences = loadMovieLens()
    # userId = str(request.user.id)
    # recommendations = getRecommendations(preferences, userId)
    # size = len(recommendations)
    # i = 0
    # while i < 5:
    #     print(recommendations[i])
    #     print('end')
    #     i = i+1
    k1,k2 = retreive(request.user)
    return render(request, 'movies/home.html', {'dict': n_list, 'moviedetails': moviedetails, 'k1': k1,'k2':k2})


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
            UserProfiles.objects.filter(user_id=request.user.id).update(genres=checked_vals)
            # n_list, moviedetails = moviedata()
            return redirect('/home')
        else:
            genreform = GenreForm()

            return render(request, 'movies/interests.html',
                          {'genreform': genreform, 'error_message': 'Select atleast one genre'})


            # return render(request, 'movies/home.html', {'dict': n_list, 'moviedetails': moviedetails})

@csrf_exempt
def rating(request):
    if request.method == 'POST':
        movieId = request.POST['movie_id']
        rating = request.POST['rating']
        userId = str(request.user.id)
        userdetails=UserProfiles.objects.filter(user_id=userId);
        print(userdetails)
        ts = time.time()
        timeStamp = int(ts)
        timeStamp=str(timeStamp)
        # fd = open('C:\\Users\\Akhilesh\\Downloads\\ml-latest\\ratings.csv', 'a')
        # mycsvrow = userId + ',' + movieId + ',' + rating + ','+timeStamp+'\n'
        # fd.write(mycsvrow)
        # fd.close()
        return HttpResponse("Success!") # Sending an success response
    else:
        return HttpResponse("Request method is not a GET")
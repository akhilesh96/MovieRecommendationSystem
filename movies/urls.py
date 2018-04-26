from django.conf.urls import url
from . import views

app_name = 'movies'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^home',views.home,name='home'),
    url(r'^search', views.search, name='search'),
    url(r'^title/(?P<movie_id>\w+)$',views.detail,name='detail'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^signup',views.signup,name='signup'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^reg_home',views.reg_home,name='reg_home'),
    url(r'^ratingurl/$' , views.rating, name='rating'),

]

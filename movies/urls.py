from django.conf.urls import url
from . import views

app_name = 'movies'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^home',views.home,name='home'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^signup',views.signup,name='signup'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^reg_home',views.reg_home,name='reg_home'),


]

# MovieRecommendationSystem
A movie recommendation system which recommends movies to users based on his interests and
ratings for different movies.

A user can login or signup into the application and initially user is asked to give his/her favourite
genres during signup and recommendations are provided based on that.

After users provide ratings to some movies, his recommendations are modified and are shown based on his/her ratings.

Typical user home page has following types of recommendations:

1) Popular Movies: The most popular english movies as per IMDB will appear here.

2) Genre Based Movies: The highly rated movies which match user's interested genres appear here.

3) User Based Movies: The Actual Recommendations based on user's ratings are shown in this category.


A user can add favourites and can give 0.2 to 5.0 rating for any movie in 0.2 increments.

PREREQUISITE: pip.

Command to install Django:
pip install django==1.11.11

Command to install django multiselect field:
pip install django-multiselectfield

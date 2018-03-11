from django import forms
from django.contrib.auth.models import User
from .models import UserProfile



class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


def selected_genres_labels(self):
    return [label for value, label in self.fields['genres'].choices if value in self['genres'].value()]

class GenreForm(forms.Form):
        OPTIONS = ((0 ,'unknown'),
               ( 1,'Action'),
               (2,'Adventure'),
               (3,'Animation'),
               (4,'Childrens'),
               (5,'Comedy'),
               (6,'Crime'),
               (7,'Documentary'),
               (8,'Drama'),
               (9,'Fantasy'),
               (10,'Film_Noir'),
               (11,'Horror'),
               (12,'Musical'),
               (13,'Mystery'),
               (14,'Romance'),
               (15,'Sci_Fi'),
               (16,'Thriller'),
               (17,'War'),
               (18,'Western'))
        genres = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                             choices=OPTIONS)

class NewForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['genres']
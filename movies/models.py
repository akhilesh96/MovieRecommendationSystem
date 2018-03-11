from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from multiselectfield import MultiSelectField

class UserProfile(models.Model):
    user = models.OneToOneField(User)

    MY_CHOICES =((0 ,'unknown'),
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

    genres = MultiSelectField(
        choices=MY_CHOICES
    )
    #other fields here

    def __str__(self):
          return "%s's profile" % self.user

def create_user_profile(sender, instance, created, **kwargs):
    if created:
       profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)
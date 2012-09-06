#!/usr/bin/env python

from datetime import datetime, timedelta
from django.utils.timezone import utc

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'applaud.settings')

from applaud import settings
import applaud.settings
from applaud import models
from django.contrib.auth.models import User, Group
from random import random
from applaud import business_views
from applaud import settings


# Standard functions
def create_thread(title, business, userprofile):
    thread = models.Thread(title=title,
                           business=business,
                           user_creator = userprofile)
    thread.save()

def create_poll(title, options, business):
    poll = models.Poll(title=title, options=options, business=business)
    poll.save()

def create_news(title, body, business):
    news=models.NewsFeedItem(title=title,
                             body=body,
                             subtitle=" ",
                             date=datetime.utcnow().replace(tzinfo=utc),
                             date_edited=datetime.utcnow().replace(tzinfo=utc),
                             business=business)
    news.save()


#########
# Agave #
#########
agave=""
user=""
try:
    agave = models.BusinessProfile.objects.get(goog_id="af55f5b087479838ebb92a86839d0f22c624ac11")
    agave.user.is_active=True
    agave.user.save()
    user=agave.user
    agave.primary_color="#4c8a3f"
    agave.save()
except models.BusinessProfile.DoesNotExist:
    user=User.objects.create_user("Agave", "joe@blackrivercafe.net", "agave")
    agave = models.BusinessProfile(user=user,
                                   goog_id="af55f5b087479838ebb92a86839d0f22c624ac11",
                                   latitude=41,
                                   longitude=-82,
                                   business_name="Agave Burrito Bar & Tequileria",
                                   primary_color="#4c8a3f",
                                   secondary_color="#f0f0f0")
    agave.save()

agave_user=""
try:
    agave_user = user.userprofile
except models.UserProfile.DoesNotExist:
    agave_user = models.UserProfile(user=user,
                                date_of_birth=datetime.utcnow().replace(tzinfo=utc),
                                first_time=0)
    agave_user.user.first_name="Slow"
    agave_user.user.last_name="Train"
    agave_user.default_picture=1;
    agave_user.save()


for item in agave.newsfeeditem_set.all():
    item.delete()

for item in agave.thread_set.all():
    item.delete()
for item in agave.poll_set.all():
    item.delete()

create_news("Agave is local!", "Agave is committed to serving food from the local community.  While this increases prices, we hope that you appreciate our commitment to buying local.", agave)
create_news("Sangria", "Don't forget we have $2 glasses and $8 pitchers of sangria", agave)
create_news("Agave was founded by an Obie!","The summer after graduating from Oberlin, Joe Waltzer (\'98) started the Black River Cafe.  He later started Agave and furthered his commitment to strengthening the local food community.", agave)
create_news("Agave is hiring", "We are currently accepting applicants for fall employment", agave)

create_thread("What should someone order who has never been to Agave?", agave, agave_user)
create_thread("Funniest things said while at Agave:", agave, agave_user)
create_thread("What is in the best burrito?", agave, agave_user)
create_thread("What type of live music would you like to hear?", agave, agave_user)
create_thread("What is your favorite thing about Agave?", agave, agave_user)
create_thread("What would you like our next sauce to be?", agave, agave_user)
create_thread("What specials would you like to see at Agave?", agave, agave_user)
create_thread("How can Agave improve?", agave, agave_user)

create_poll("How much extra would you pay if Agave delivered?", ['Under 5%', '10%', '15%', 'Over 20%'], agave)
create_poll("What do you prefer at Agave?", ['Chicken', 'Pork', 'Beef', 'Steak', 'Grilled Vegetables'], agave)
create_poll("What is your favorite Agave special?", ["Monday: $4 Long Islands", "Tuesday: $1 off draft beer and well drinks", "Wednesday: 8-10 happy hour - $1 well drinks", "Thursday: $4 margaritas, $5.50 super margaritas", "Friday: $1 off pints, $1.50 off mugs", "Saturday: $3 for 2 Jell-O shots", "Sunday: Sangria - $2 glass, $3 pitcher"], agave)
create_poll("Which is the best day of the week for live music?", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], agave)




# ##############
# # Slow Train #
# ##############

# # Need to change this when running on the server
# st_user=""
# try:
#     slowtrain = models.BusinessProfile.objects.get(goog_id="cd4842ff78103167deeaf236fd198dd59b88ad78")
#     st_user=slowtrain.user
# except models.BusinessProfile.DoesNotExist:
#     st_user = User.objects.create_user('Slow Train', 'jessa@slowtraincafe.com', 'oclove')
#     slowtrain = models.BusinessProfile(user=st_user,
#                                        latitude = 41.291624,
#                                        longitude = -82.215433,
#                                        goog_id="cd4842ff78103167deeaf236fd198dd59b88ad78",
#                                        business_name="The Slow Train Cafe",
#                                        primary_color="#873920",
#                                        secondary_color="#f0f0f0")
#     slowtrain.save()

# st = models.BusinessProfile(user=slowtrain.user,
#                             latitude = slowtrain.latitude, 
#                             longitude = slowtrain.longitude,
#                             goog_id = slowtrain.goog_id,
#                             business_name = slowtrain.business_name,
#                             primary_color = slowtrain.primary_color,
#                             secondary_color = slowtrain.secondary_color)
# slowtrain.delete()
# st.save()

# st_userprofile = User.objects.get(username="slowtrain_user").userprofile
# # st_userprofile = models.UserProfile(user=User.objects.create_user("slowtrain_user", 'jessa@slowtraincafe.com', 'oclove'),
# #                                     date_of_birth=datetime.utcnow().replace(tzinfo=utc),
# #                                     first_time=0)
# # st_userprofile.user.first_name="Slow"
# # st_userprofile.user.last_name="Train"
# # st_userprofile.default_picture=1;
# # st_userprofile.save()


# # NewsFeedItems
# nf1 = models.NewsFeedItem(title="The Slow (Food) Train",
#                           body="All of our food is prepared fresh, throughout each week, by local chefs and bakers who use wholesome, all-natural ingredients, utilizing local farms and sustainable resources whenever possible.",
#                           date=datetime.utcnow().replace(tzinfo=utc),
#                           date_edited=datetime.utcnow().replace(tzinfo=utc),
#                           subtitle=" ",
#                           business=st)
# nf1.save()

# nf2 = models.NewsFeedItem(title="Wine Night every Tuesday and Thursday",
#                           body="From 4pm to close. $3 glasses and cocktails!",
#                           subtitle=" ",
#                           date=datetime.utcnow().replace(tzinfo=utc),
#                           date_edited=datetime.utcnow().replace(tzinfo=utc),
#                           business=st)
# nf2.save()

# nf3 = models.NewsFeedItem(title="The Slow Train is expanding",
#                           body="Starting this fall, you can swing by our coffee bar across the street from The Feve",
#                           subtitle=" ",
#                           date=datetime.utcnow().replace(tzinfo=utc),
#                           date_edited=datetime.utcnow().replace(tzinfo=utc),
#                           business=st)
# nf3.save()

# nf4 = models.NewsFeedItem(title="If you would like us to display your art, set up a show or event...",
#                           body="Please email ztesler@gmail.com",
#                           subtitle=" ",
#                           date=datetime.utcnow().replace(tzinfo=utc),
#                           date_edited=datetime.utcnow().replace(tzinfo=utc),
#                           business=st)
# nf4.save()

# nf5 = models.NewsFeedItem(title="Draw a mural on our chalkboard!",
#                           body="To sign up, please email josh@slowtraincafe.com",
#                           subtitle=" ",
#                           date=datetime.utcnow().replace(tzinfo=utc),
#                           date_edited=datetime.utcnow().replace(tzinfo=utc),
#                           business=st)
# nf5.save()

# nf6 = models.NewsFeedItem(title="We have switched to plastic cups",
#                           body="We have switched because too many glasses were taken from Slow Train.  We would love to hear your suggestions for environmental sustainability at the Slow Train, including strategies for returning to glassware.",
#                           subtitle=" ",
#                           date=datetime.utcnow().replace(tzinfo=utc),
#                           date_edited=datetime.utcnow().replace(tzinfo=utc),
#                           business=st)
# nf6.save()

# nf7 = models.NewsFeedItem(title="The Slow Train was started by Oberlin alumni!",
#                           body="Jessa New (\'01) and Zach Tesler (\'07) partnered up to start the Slow Train in 2010.",
#                           subtitle=" ",
#                           date=datetime.utcnow().replace(tzinfo=utc),
#                           date_edited=datetime.utcnow().replace(tzinfo=utc),
#                           business=st)
# nf7.save()


# # Creating mingle threads

# create_thread("What is the best thing to order at Slow Train?",st, st_userprofile)
# create_thread("What events do you wish took place at Slow Train?", st, st_userprofile)
# create_thread("What do you think of the remodel?", st, st_userprofile)
# create_thread("Is there anything you would like to see improve abouut Slow Train?", st, st_userprofile)
# create_thread("Best live music you have seen at Slow Train", st, st_userprofile)
# create_thread("What contests should Slow Train hold?", st, st_userprofile)
# create_thread("What tea do you wish we served here?", st, st_userprofile)
# create_thread("If the Slow Train were a train where would you want it to be taking you right now?", st, st_userprofile)


# # Polls 

# create_poll("What's your favorite coffee?", 
#             ['Gothic', 'Mexican', 'Sumatran', 'Market', 'Costa Rican', 'Tanzanian', 'Ethiopian', 'Firehouse'], st)

# create_poll("Why do you typically come to Slow Train?",
#             ['Coffee','Food','Place to do work','Live Music'],st)

# create_poll("Would you come to an art walk twice a semester?",
#             ['Yes','No'], st)

# create_poll("Would you rather have a Slow Train...",
#             ['Swing dance night', 'Jazz dance night', 'Art walk night', 'Movie night', 'Dominion night'], st)




# #############
# # The Feve ##
# #############




# # Need to change this when running on the server
# feve_user=""
# try:
#     thefeve = models.BusinessProfile.objects.get(goog_id="90337243a42c2dc414a467d8ec6fc09746a2f03d")
#     feve_user = thefeve.user
# except models.BusinessProfile.DoesNotExist:
#     feve_user = User.objects.create_user('The Feve', 'jayfeve@gmail.com', 'feve')
#     thefeve = models.BusinessProfile(user=feve_user,
#                                      latitude = 41.290828,
#                                      longitude = -82.21759,
#                                      goog_id="90337243a42c2dc414a467d8ec6fc09746a2f03d",
#                                      business_name="The Feve",
#                                      primary_color="#873920",
#                                      secondary_color="#f0f0f0")

# # Changing the colors for when we get it from the business profiles already in the server
# thefeve.primary_color="#873920"
# thefeve.secondary_color="#f0f0f0"
# thefeve.save()

# feve = models.BusinessProfile(user=thefeve.user,
#                             latitude = thefeve.latitude, 
#                             longitude = thefeve.longitude,
#                             goog_id = thefeve.goog_id,
#                             business_name = thefeve.business_name,
#                             primary_color = thefeve.primary_color,
#                             secondary_color = thefeve.secondary_color)
# thefeve.delete()
# feve.save()

# feve_userprofile = User.objects.get(username="The Feve").userprofile
# # feve_userprofile = models.UserProfile(user=feve_user,
# #                                     date_of_birth=datetime.utcnow().replace(tzinfo=utc),
# #                                     first_time=0)
# # feve_userprofile.default_picture=1;
# # feve_userprofile.save()


# create_news("The Feve party room",
#             "Soon the Feve\'s party room will be available for private events and more space for drinking!  If you would like to inquire about booking the room, please contact Jason: jayfeve@gmail.com",
#             feve)

# create_news("Upstairs Specials",
#             "Monday: All night happy hour. Tuesday: $4 for ten wings. Wednesday: Long Islands. Thursday: Shots and Tots. Friday: Happy happy hour. Saturday: $5 shot and a beer",
#             feve)

# create_news("Artists/Musicians!",
#             "If you would like to have your art on the walls, or to play a show at the Feve, please contact Jason: jayfeve@gmail.com",
#             feve)


# create_thread("What is the best thing to order at the Feve?", feve, feve_userprofile)
# create_thread("How could the Feve improve?", feve, feve_userprofile)
# create_thread("What is your favorite part of the Feve?", feve, feve_userprofile)
# create_thread("What are your opinions on the Feve art?", feve, feve_userprofile)
# create_thread("Would you rather...", feve, feve_userprofile)
# create_thread("Best bar tricks", feve, feve_userprofile)
# create_thread("What should the Feve drinking game be?", feve, feve_userprofile)
# create_thread("The best Feve brunch dishes", feve, feve_userprofile)
# create_thread("What should Feve brunch do next?", feve, feve_userprofile)

# create_poll("Did you get your free drink on your 21st birthday?",
#             ['Yes','No'], feve)
# create_poll("What events would you like to have hosten in the Feve party room?",
#             ['Fancy Cocktail Hour', 'Jazz Dance', 'Swing Dance', 'Beer Olympics', 'Poker Night'], feve)
# create_poll("What is your favorite special night?",
#             ['Monday: All night happy hour', 'Tuesday: Shots-n-tots', 
#              'Wednesday: Long Islands', 'Thursday: Wings', 'Friday: Happy Happy hour',
#              'Saturday: Shot and a beer'], feve)
# create_poll("What is your favourite music to hear live at the Feve", 
#             ['Jazz','Acoustic','Rock','Metal'], feve)





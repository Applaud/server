#!/usr/bin/env python

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'applaud.settings')

from django.utils.timezone import utc
from datetime import datetime, timedelta
from applaud import settings
import applaud.settings
from applaud import models
from django.contrib.auth.models import User, Group

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


with open('apatapa_places.txt') as f:
    for line in f:

        line = line.strip()
        parts = line.split(',')
        
        name = parts[0]
        lat = float(parts[1])
        lon = float(parts[2])

        user = User.objects.create_user(name, 'apatapa@apatapa.com', 'applaud')
        
        business = models.BusinessProfile(user=user, phone='', latitude=lat, longitude=lon, goog_id='', business_name=name, isGoog=0, isApplaud=0, isNewsfeed=0, isPolls=0)
        business.save()
        
        # Hash to get the fake google id?
        # In the meantime just use the pk

        biz_id = business.id
        business.goog_id = biz_id
        business.save()

#####################################
# INDIVIDUAL LOCATIONS WITH CONTENT #
#####################################

# Make and seed Agave
user = User.objects.create_user("Agave", "apatapa@apatapa.com", 'applaud')

business = models.BusinessProfile(user=user, phone='', latitude=41.291488, longitude=-82.218032, goog_id='', business_name="Agave", isGoog=0, isApplaud=0)
business.save()

agave_user = models.UserProfile(user=user,
                                date_of_birth=datetime.utcnow().replace(tzinfo=utc),
                                first_time=0)
agave_user.user.first_name="Agave"
agave_user.user.last_name=""
agave_user.default_picture=1;
agave_user.save()
        
# Hash to get the fake google id?
# In the meantime just use the pk

biz_id = business.id
business.goog_id = biz_id
business.save()

create_news("Agave is local!", "Agave is committed to serving food from the local community.  While this increases prices, we hope that you appreciate our commitment to buying local.", business)
create_news("Sangria", "Don't forget we have $2 glasses and $8 pitchers of sangria", business)
create_news("Agave was founded by an Obie!","The summer after graduating from Oberlin, Joe Waltzer (\'98) started the Black River Cafe.  He later started Agave and furthered his commitment to strengthening the local food community.", business)
create_news("Agave is hiring", "We are currently accepting applicants for fall employment", business)

create_thread("What should someone order who has never been to Agave?", business, agave_user)
create_thread("Funniest things said while at Agave:",business, agave_user)
create_thread("What is in the best burrito?", business, agave_user)
create_thread("What type of live music would you like to hear?", business, agave_user)
create_thread("What is your favorite thing about Agave?", business, agave_user)
create_thread("What would you like our next sauce to be?", business, agave_user)
create_thread("What specials would you like to see at Agave?", business, agave_user)
create_thread("How can Agave improve?", business, agave_user)

create_poll("How much extra would you pay if Agave delivered?", ['Under 5%', '10%', '15%', 'Over 20%'], business)
create_poll("What do you prefer at Agave?", ['Chicken', 'Pork', 'Beef', 'Steak', 'Grilled Vegetables'], business)
create_poll("What is your favorite Agave special?", ["Monday: $4 Long Islands", "Tuesday: $1 off draft beer and well drinks", "Wednesday: 8-10 happy hour - $1 well drinks", "Thursday: $4 margaritas, $5.50 super margaritas", "Friday: $1 off pints, $1.50 off mugs", "Saturday: $3 for 2 Jell-O shots", "Sunday: Sangria - $2 glass, $3 pitcher"], business)
create_poll("Which is the best day of the week for live music?", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], business)

# Make Feve
user = User.objects.create_user("Feve", "apatapa@apatapa.com", 'applaud')

feve = models.BusinessProfile(user=user, phone='', latitude=41.290827, longitude=-82.217555, goog_id='', business_name="Feve", isGoog=0, isApplaud=0)
feve.save()
    
feve_userprofile = models.UserProfile(user=user,
                                date_of_birth=datetime.utcnow().replace(tzinfo=utc),
                                first_time=0)
feve_userprofile.user.first_name="Feve"
feve_userprofile.user.last_name=""
feve_userprofile.default_picture=1;
feve_userprofile.save()

    
# Hash to get the fake google id?
# In the meantime just use the pk

biz_id = feve.id
feve.goog_id = biz_id
feve.save()

create_news("The Feve party room",
            "Soon the Feve\'s party room will be available for private events and more space for drinking!  If you would like to inquire about booking the room, please contact Jason: jayfeve@gmail.com",
            feve)

create_news("Upstairs Specials",
            "Monday: All night happy hour. Tuesday: $4 for ten wings. Wednesday: Long Islands. Thursday: Shots and Tots. Friday: Happy happy hour. Saturday: $5 shot and a beer",
            feve)

create_news("Artists/Musicians!",
            "If you would like to have your art on the walls, or to play a show at the Feve, please contact Jason: jayfeve@gmail.com",
            feve)


create_thread("What is the best thing to order at the Feve?", feve, feve_userprofile)
create_thread("How could the Feve improve?", feve, feve_userprofile)
create_thread("What is your favorite part of the Feve?", feve, feve_userprofile)
create_thread("What are your opinions on the Feve art?", feve, feve_userprofile)
create_thread("Would you rather...", feve, feve_userprofile)
create_thread("Best bar tricks", feve, feve_userprofile)
create_thread("What should the Feve drinking game be?", feve, feve_userprofile)
create_thread("The best Feve brunch dishes", feve, feve_userprofile)
create_thread("What should Feve brunch do next?", feve, feve_userprofile)

create_poll("Did you get your free drink on your 21st birthday?",
            ['Yes','No'], feve)
create_poll("What events would you like to have hosten in the Feve party room?",
            ['Fancy Cocktail Hour', 'Jazz Dance', 'Swing Dance', 'Beer Olympics', 'Poker Night'], feve)
create_poll("What is your favorite special night?",
            ['Monday: All night happy hour', 'Tuesday: Shots-n-tots', 
             'Wednesday: Long Islands', 'Thursday: Wings', 'Friday: Happy Happy hour',
             'Saturday: Shot and a beer'], feve)
create_poll("What is your favourite music to hear live at the Feve", 
            ['Jazz','Acoustic','Rock','Metal'], feve)


# Make Slow Train
user = User.objects.create_user("Slow Train", "apatapa@apatapa.com", 'applaud')

st = models.BusinessProfile(user=user, phone='', latitude=41.291613, longitude=-82.215428, goog_id='', business_name="The Slow Train Cafe", isGoog=0, isApplaud=0)
st.save()

st_userprofile = models.UserProfile(user=user,
                                date_of_birth=datetime.utcnow().replace(tzinfo=utc),
                                first_time=0)
st_userprofile.user.first_name="Slow"
st_userprofile.user.last_name="Train"
st_userprofile.default_picture=1;
st_userprofile.save()


biz_id = st.id
st.goog_id = biz_id
st.save()


# NewsFeedItems
nf1 = models.NewsFeedItem(title="The Slow (Food) Train",
                          body="All of our food is prepared fresh, throughout each week, by local chefs and bakers who use wholesome, all-natural ingredients, utilizing local farms and sustainable resources whenever possible.",
                          date=datetime.utcnow().replace(tzinfo=utc),
                          date_edited=datetime.utcnow().replace(tzinfo=utc),
                          subtitle=" ",
                          business=st)
nf1.save()

nf2 = models.NewsFeedItem(title="Wine Night every Tuesday and Thursday",
                          body="From 4pm to close. $3 glasses and cocktails!",
                          subtitle=" ",
                          date=datetime.utcnow().replace(tzinfo=utc),
                          date_edited=datetime.utcnow().replace(tzinfo=utc),
                          business=st)
nf2.save()

nf3 = models.NewsFeedItem(title="The Slow Train is expanding",
                          body="Starting this fall, you can swing by our coffee bar across the street from The Feve",
                          subtitle=" ",
                          date=datetime.utcnow().replace(tzinfo=utc),
                          date_edited=datetime.utcnow().replace(tzinfo=utc),
                          business=st)
nf3.save()

nf4 = models.NewsFeedItem(title="If you would like us to display your art, set up a show or event...",
                          body="Please email ztesler@gmail.com",
                          subtitle=" ",
                          date=datetime.utcnow().replace(tzinfo=utc),
                          date_edited=datetime.utcnow().replace(tzinfo=utc),
                          business=st)
nf4.save()

nf5 = models.NewsFeedItem(title="Draw a mural on our chalkboard!",
                          body="To sign up, please email josh@slowtraincafe.com",
                          subtitle=" ",
                          date=datetime.utcnow().replace(tzinfo=utc),
                          date_edited=datetime.utcnow().replace(tzinfo=utc),
                          business=st)
nf5.save()

nf6 = models.NewsFeedItem(title="We have switched to plastic cups",
                          body="We have switched because too many glasses were taken from Slow Train.  We would love to hear your suggestions for environmental sustainability at the Slow Train, including strategies for returning to glassware.",
                          subtitle=" ",
                          date=datetime.utcnow().replace(tzinfo=utc),
                          date_edited=datetime.utcnow().replace(tzinfo=utc),
                          business=st)
nf6.save()

nf7 = models.NewsFeedItem(title="The Slow Train was started by Oberlin alumni!",
                          body="Jessa New (\'01) and Zach Tesler (\'07) partnered up to start the Slow Train in 2010.",
                          subtitle=" ",
                          date=datetime.utcnow().replace(tzinfo=utc),
                          date_edited=datetime.utcnow().replace(tzinfo=utc),
                          business=st)
nf7.save()


# Creating mingle threads

create_thread("What is the best thing to order at Slow Train?",st, st_userprofile)
create_thread("What events do you wish took place at Slow Train?", st, st_userprofile)
create_thread("What do you think of the remodel?", st, st_userprofile)
create_thread("Is there anything you would like to see improve abouut Slow Train?", st, st_userprofile)
create_thread("Best live music you have seen at Slow Train", st, st_userprofile)
create_thread("What contests should Slow Train hold?", st, st_userprofile)
create_thread("What tea do you wish we served here?", st, st_userprofile)
create_thread("If the Slow Train were a train where would you want it to be taking you right now?", st, st_userprofile)


# Polls 

create_poll("What's your favorite coffee?", 
            ['Gothic', 'Mexican', 'Sumatran', 'Market', 'Costa Rican', 'Tanzanian', 'Ethiopian', 'Firehouse'], st)

create_poll("Why do you typically come to Slow Train?",
            ['Coffee','Food','Place to do work','Live Music'],st)

create_poll("Would you come to an art walk twice a semester?",
            ['Yes','No'], st)

create_poll("Would you rather have a Slow Train...",
            ['Swing dance night', 'Jazz dance night', 'Art walk night', 'Movie night', 'Dominion night'], st)


# Make the omnipresent Apatapa Feedback
user = User.objects.create_user("Feedback", 'apatapa@apatapa.com', 'applaud')
        
business = models.BusinessProfile(user=user, phone='', latitude=lat, longitude=lon, goog_id='8eaccc6443d4a16442baf5f3a0bd527594105436', business_name="Apatapa Feedback", isGoog=0, isApplaud=0, isNewsfeed=0)
business.save()



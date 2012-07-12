#!/usr/bin/env python

from datetime import datetime, timedelta
from django.utils.timezone import utc

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'applaud.settings')

import applaud.settings
from applaud import models
from django.contrib.auth.models import User, Group
from random  import random

# Make a User.
user = User.objects.create_user('Boo Furgers', 'boofurgers@aol.com', 'applaud')
user2 = User.objects.create_user('Apatapa', 'alsdafasdf@gmail.com', 'applaud')
enduser = User.objects.create_user('Master Trash', 'mastertrash@gmail.com', 'seekrit')
enduser.first_name="Master"
enduser.last_name="Trash"
enduser.save()
# Make another user.
enduser2 = User.objects.create_user('Mama Bear', 'mamabear@berensteinbears.com', 'seekrit')
enduser2.first_name="Mama"
enduser2.last_name="Bear"
enduser2.save()

keith_user = User.objects.create_user('Keith', 'foo@bar.com', 'apatapa')
keith_user.first_name = 'Keith'
keith_user.last_name = 'Cox'
keith_user.save()

# Make userprofile (he's really young, I know...)
userprofile = models.UserProfile(user=enduser,
                                 date_of_birth=datetime.utcnow().replace(tzinfo=utc),
                                 first_time=0)
userprofile.save()
userprofile2 = models.UserProfile(user=enduser2,
                                 date_of_birth=datetime.utcnow().replace(tzinfo=utc),
                                 first_time=0)
userprofile2.save()


# Make a BusinessProfile.
business = models.BusinessProfile(user=user, phone='1.123.123.1234', latitude=39.07279, longitude=-120.14223, goog_id="677679492a58049a7eae079e0890897eb953d79b", business_name="Boo Furgers")
business.save()
business2 = models.BusinessProfile(user=user2, phone='0-987-654-3210', latitude=39.07279, longitude=-120.14223, goog_id='asdf987sdf765asdf875asdf685487we65r9867', business_name='Apatapa')
business2.save()
keith_business = models.BusinessProfile(user=keith_user, phone='1-585-385-2224',
                                        latitude='14.3', longitude='12.34',
                                        goog_id='23l;asdr4ajiaf', business_name="Resort Equities")

# Business and Customer groups.
business_group = Group(name='Business')
business_group.save()
customer_group = Group(name='Customer')
customer_group.save()

# Add the business group.
business.groups = [business_group]
business.save()
keith_business.groups = [business_group]
keith_business.save()
business2.groups = [business_group]
business2.save()

# Make a RatingProfile.

profile1 = models.RatingProfile(title='Profile 1', business=business)
profile1.save()
slickness = models.RatedDimension(title="Slickness",
                           rating_profile=profile1)
awesomeness = models.RatedDimension(title="Awesomeness",
                             rating_profile=profile1)
slickness.save()
awesomeness.save()

profile2 = models.RatingProfile(title='Profile 2', business=business2)
profile2.save()
efficiency = models.RatedDimension(title="Efficiency",
                                   rating_profile=profile2,
                                   is_text=True)
enthusiasm = models.RatedDimension(title="Enthusiasm",
                             rating_profile=profile2)
efficiency.save()
enthusiasm.save()

keith_waiter_profile = models.RatingProfile(title='Waiter', business=keith_business)
keith_waiter_profile.save()
promptness = models.RatedDimension(title='Promptness',
                                   rating_profile=keith_waiter_profile)
promptness.save()
friendliness = models.RatedDimension(title='Friendliness',
                                     rating_profile=keith_waiter_profile)
friendliness.save()
helpfulness = models.RatedDimension(title='Helpfulness',
                                    rating_profile=keith_waiter_profile)
helpfulness.save()

keith_hostess_profile = models.RatingProfile(title='Hostess', business=keith_business)
friendliness = models.RatedDimension(title='Friendliness',
                                     rating_profile=keith_hostess_profile)
friendliness.save()
helpfulness = models.RatedDimension(title='Helpfulness',
                                    rating_profile=keith_hostess_profile)
helpfulness.save()
two_adj = models.RatedDimension(title='Describe with two adjectives',
                                rating_profile=keith_hostess_profile,
                                is_text=True)
two_adj.save()


profile3 = models.RatingProfile(title='Profile 3', business=business)
profile3.save()
slipperiness = models.RatedDimension(title="Slipperiness",
                           rating_profile=profile3)
surliness = models.RatedDimension(title="Surliness",
                             rating_profile=profile3)
slipperiness.save()
surliness.save()

# Make a User.
emp_user = User.objects.create_user('joe', 'joes@aol.com', 'apatapa')
emp_user.first_name = 'Moe'
emp_user.last_name = 'Smith'
emp_user.save()
emp_user2 = User.objects.create_user('Jill', 'jill@gmail.com', 'apatapa')
emp_user2.first_name = 'Jill'
emp_user2.last_name = 'Lane'
emp_user2.save()
emp_user3 = User.objects.create_user('jeremy', 'jeremy@aol.com', 'apatapa')
emp_user3.first_name = 'Jeremy'
emp_user3.last_name = 'Bates'
emp_user3.save()
emp_enduser = User.objects.create_user('josh', 'josh@gmail.com', 'apatapa')
emp_enduser.first_name = 'Josh'
emp_enduser.last_name = 'Englewood'
emp_enduser.save()

#Lots of employees for Boo Furgers!
emp_user6 = User.objects.create_user('jordan', 'jordan@aol.com', 'apatapa')
emp_user6.first_name = 'Jordan'
emp_user6.last_name = 'Moon'
emp_user6.save()
emp_user4 = User.objects.create_user('jack', 'jackjones@aol.com', 'apatapa')
emp_user4.first_name = 'Jack'
emp_user4.last_name = 'Jones'
emp_user4.save()
emp_user5 = User.objects.create_user('LaLa', 'lala@aol.com', 'apatapa')
emp_user5.first_name = 'Sarah'
emp_user5.last_name = 'Jane'
emp_user5.save()


# Make a few Employees.
master = models.EmployeeProfile(business=business,
                                user=emp_user,
                                rating_profile=profile2,
                                bio='foo')
master.save()
mystical = models.EmployeeProfile(business=business2,
                                  user=emp_user2,
                                  rating_profile=profile2,
                                  bio='bio')
mystical.save()
mystical2 = models.EmployeeProfile(business=business,
                                  user=emp_user3,
                                  rating_profile=profile3,
                                  bio='bio')
mystical2.save()
luke = models.EmployeeProfile(business=business2,
                              user=emp_enduser,
                              rating_profile=profile3,
                              bio='biology')
luke.save()

mystical2 = models.EmployeeProfile(business=business,
                                  user=emp_user6,
                                  rating_profile=profile1,
                                  bio="Super super bio!!!!!")
mystical2.save()

mystical2 = models.EmployeeProfile(business=business,
                                  user=emp_user4,
                                  rating_profile=profile1,
                                  bio='The bioiest of all bioed bios')
mystical2.save()

mystical2 = models.EmployeeProfile(business=business,
                                  user=emp_user5,
                                  rating_profile=profile3,
                                  bio="Another lovely bio for another employee of the month! Ring the bell, hit the gong, we\'ve got a superstar on our hands! Remember back when you were just a kid??")
mystical2.save()

moe = models.EmployeeProfile(business=keith_business,
                             user=emp_user,
                             rating_profile=keith_waiter_profile,
                             bio='Moe grew up in South San Francisco, went to Cal, and began working at Pacific Catch in 2010. Moe hopes to get his master\'s and work in restaurant management.')
moe.save()
jill = models.EmployeeProfile(business=keith_business,
                              user=emp_user2,
                              rating_profile=keith_hostess_profile,
                              bio='Jill is from Denmark. She currently goes to art school and is studying portraiture.')
jill.save()
jeremy = models.EmployeeProfile(business=keith_business,
                                user=emp_user3,
                                rating_profile=keith_waiter_profile,
                                bio='After graduating from Oberlin College in 1993, Jeremy tried his hand at microbrewing, but found it much too small. He is our oldest employee, and dreams of owning his own restaurant.')
jeremy.save()
josh = models.EmployeeProfile(business=keith_business,
                              user=emp_enduser,
                              rating_profile=keith_hostess_profile,
                              bio='')

# Make some Ratings. Only "master" has ratings.
# 'master' can be rated on 'awesomeness' and 'slickness'
quality_dim = profile1.rateddimension_set.get(title='Quality')
for i in range(10):
    today = datetime.utcnow().replace(tzinfo=utc)+timedelta(days=i)
    print today
    rating1 = models.Rating(title='Awesomeness',
                            rating_value=5*random(),
                            employee=master,
#                            id=1,
                            date_created=today,
                            dimension=awesomeness,
                            user=userprofile)
    rating1.save()
    rating2 = models.Rating(title='Slickness',
                            rating_value=5*random(),
                            employee=master,
                            date_created=today,
                            dimension=slickness,
                            user=userprofile)
    rating2.save()
    rating3 = models.Rating(title='Quality',
                            rating_value=5*random(),
                            employee=master,
                            date_created=today,
                            dimension=quality_dim,
                            user=userprofile)
    rating3.save()

# Make a couple of NewsFeedItems.
nfi1 = models.NewsFeedItem(title='Apatapa arrives in Tahoe!',
                           subtitle='proceed to code',
                           body='After an insane amout of driving, we finally got there.',
                           date=datetime.utcnow().replace(tzinfo=utc),
                           date_edited=datetime.utcnow().replace(tzinfo=utc),
                           business=business)

nfi1.save()
nfi2 = models.NewsFeedItem(title='Foo!',
                           subtitle='Bar?',
                           body='Baz.',
                           date=datetime.utcnow().replace(tzinfo=utc),
                           date_edited=datetime.utcnow().replace(tzinfo=utc),
                           business=business)
nfi2.save()
nfi3 = models.NewsFeedItem(title='Try our new parrots!',
                           subtitle='Delicious, nutritious.',
                           body='These parrots are selling for a dollar.',
                           date=datetime.utcnow().replace(tzinfo=utc),
                           date_edited=datetime.utcnow().replace(tzinfo=utc),
                           business=business)
nfi3.save()

# Make Surveys.
s1 = models.Survey(title='Emacs?', description='Text editor of the gods.', business=business)
s1.save()
s2 = models.Survey(title='Apatapa?', description='Apps providing apatapa through apps providing apatapa', business=business2)
s2.save()

# Make Questions.
q1 = models.Question(label='Yes or no?', type='RG', options=['yes', 'no'], survey=s1)
q1.save()
q2 = models.Question(label='African swallow or European swallow?', type='CG', options=['yes', 'no'], survey=s1)
q2.save()
q3 = models.Question(label='What is your favorite color?', type='TF', options=[], survey=s1)
q3.save()
q4 = models.Question(label='Tell us your life story', type='TA', survey=s1)
q4.save()

# Write responses.
qr1 = models.QuestionResponse(question=q1,
                              response=['yes'],
                              date_created=datetime.utcnow().replace(tzinfo=utc),
                              user=userprofile)
qr1.save()

for i in range(10):
    today = datetime.utcnow().replace(tzinfo=utc)+timedelta(days=i)
    options = ["yes","no"]
    profiles = [userprofile,userprofile2]
    which = options[int(2*random())]
    qr2 = models.QuestionResponse(question=q2,
                                  response=[which],
                                  date_created=today,
                                  user=profiles[int(random()*2)])
    qr2.save()

,qr3 = models.QuestionResponse(question=q3,
                              response=['aaargh!'],
                              date_created=datetime.utcnow().replace(tzinfo=utc),
                              user=userprofile)
qr3.save()
qr4 = models.QuestionResponse(question=q4,
                              response=['Life story HERE.'],
                              date_created=datetime.utcnow().replace(tzinfo=utc),
                              user=userprofile)
qr4.save()


print 'apatapa!'

#!/usr/bin/env python

from datetime import datetime

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'applaud.settings')

import applaud.settings
from applaud import models
from django.contrib.auth.models import User, Group

# Make a User.
user = User.objects.create_user('Boo Furgers', 'boofurgers@aol.com', 'applaud')
user2 = User.objects.create_user('Apatapa', 'alsdafasdf@gmail.com', 'applaud')
enduser = User.objects.create_user('Master Trash', 'mastertrash@gmail.com', 'seekrit')

# Make userprofile (he's really young, I know...)
userprofile = models.UserProfile(user=enduser,
                                 date_of_birth=datetime.now(),
                                 first_time=0)
userprofile.save()

# Make a BusinessProfile.
business = models.BusinessProfile(user=user, phone='1.123.123.1234', latitude=12.345, longitude=234.23423, goog_id="677679492a58049a7eae079e0890897eb953d79b")
business.save()
business2 = models.BusinessProfile(user=user2, phone='0-987-654-3210', latitude=9.2342, longitude=6272.43814, goog_id='asdf987sdf765asdf875asdf685487we65r9867')
business2.save()

# Business and Customer groups.
business_group = Group(name='Business')
business_group.save()
customer_group = Group(name='Customer')
customer_group.save()

# Add the business group.
business.groups = [business_group]
business.save()
business2.groups = [business_group]
business2.save()

# Make a RatingProfile.
profile1 = models.RatingProfile(title='Profile 1', dimensions=['Slickness', 'Awesomeness'], business=business)
profile1.save()
profile2 = models.RatingProfile(title='Profile 2', dimensions=['Efficiency', 'Enthusiasm', 'Sarcasm'], business=business2)
profile2.save()
profile3 = models.RatingProfile(title='Profile 3', dimensions=['Slipperiness', 'Surliness'], business=business)
profile3.save()

# Make a User.
emp_user = User.objects.create_user('joe', 'joes@aol.com', 'apatapa')
emp_user.first_name = 'joe'
emp_user.last_name = 'jake'
emp_user.save()
emp_user2 = User.objects.create_user('jill', 'jill@gmail.com', 'apatapa')
emp_user2.first_name = 'jill'
emp_user2.last_name = 'joan'
emp_user2.save()
emp_user3 = User.objects.create_user('jeremy', 'jeremy@aol.com', 'apatapa')
emp_user3.first_name = 'jeremy'
emp_user3.last_name = 'jewelthief'
emp_user3.save()
emp_enduser = User.objects.create_user('josh', 'josh@gmail.com', 'apatapa')
emp_enduser.first_name = 'josh'
emp_enduser.last_name = 'jeff'
emp_enduser.save()

# Make a few Employees.
master = models.EmployeeProfile(business=business,
                                user=emp_user,
                                rating_profile=profile1,
                                bio='foo')
master.save()
mystical = models.EmployeeProfile(business=business2,
                                  user=emp_user2,
                                  rating_profile=profile2,
                                  bio='bio')
mystical.save()
mystical2 = models.EmployeeProfile(business=business,
                                  user=emp_user3,
                                  rating_profile=profile1,
                                  bio='bio')
mystical2.save()
luke = models.EmployeeProfile(business=business2,
                              user=emp_enduser,
                              rating_profile=profile3,
                              bio='biology')
luke.save()

# Make some Ratings. Only "master" has ratings.
# 'master' can be rated on 'awesomeness' and 'slickness'
rating1 = models.Rating(title='Awesomeness',
                        rating_value=5,
                        employee=master,
                        id=1,
                        date_created=datetime.now(),
                        user=userprofile)
rating1.save()
rating2 = models.Rating(title='Slickness',
                        rating_value=5,
                        employee=master,
                        date_created=datetime.now(),
                        user=userprofile)
rating2.save()
rating3 = models.Rating(title='Slickness',
                        rating_value=4,
                        employee=master,
                        date_created=datetime.now(),
                        user=userprofile)
rating3.save()
rating4 = models.Rating(title='Slickness',
                        rating_value=4,
                        employee=master,
                        date_created=datetime.now(),
                        user=userprofile)
rating4.save()

# Make a couple of NewsFeedItems.
nfi1 = models.NewsFeedItem(title='Apatapa arrives in Tahoe!',
                           subtitle='proceed to code',
                           body='After an insane amout of driving, we finally got there.',
                           date=datetime.now(),
                           date_edited=datetime.now(),
                           business=business)

nfi1.save()
nfi2 = models.NewsFeedItem(title='Foo!',
                           subtitle='Bar?',
                           body='Baz.',
                           date=datetime.now(),
                           date_edited=datetime.now(),
                           business=business)
nfi2.save()
nfi3 = models.NewsFeedItem(title='Try our new parrots!',
                           subtitle='Delicious, nutritious.',
                           body='These parrots are selling for a dollar.',
                           date=datetime.now(),
                           date_edited=datetime.now(),
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
q3 = models.Question(label='What is your favorite color?', type='TF', options=['blue', 'yellow', 'aaargh!'], survey=s1)
q3.save()
q4 = models.Question(label='Tell us your life story', type='TA', survey=s1)
q4.save()

# Write responses.
qr1 = models.QuestionResponse(question=q1,
                              response=['yes'],
                              date_created=datetime.now(),
                              user=userprofile)
qr1.save()
qr2 = models.QuestionResponse(question=q2,
                              response=['no'],
                              date_created=datetime.now(),
                              user=userprofile)
qr2.save()
qr3 = models.QuestionResponse(question=q3,
                              response=['aaargh!'],
                              date_created=datetime.now(),
                              user=userprofile)
qr3.save()
qr4 = models.QuestionResponse(question=q4,
                              response=['Life story HERE.'],
                              date_created=datetime.now(),
                              user=userprofile)
qr4.save()


print 'apatapa!'

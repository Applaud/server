#!/usr/bin/env python

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'applaud.settings')

import applaud.settings
from applaud import models
import datetime
from django.contrib.auth.models import User, Group

# Make a User.
user = User.objects.create_user('Boo Furgers', 'boofurgers@aol.com', 'applaud')
user2 = User.objects.create_user('Apatapa', 'alsdafasdf@gmail.com', 'applaud')
enduser = User.objects.create_user('Master Trash', 'mastertrash@gmail.com', 'seekrit')

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
profile1 = models.RatingProfile(title='Profile 1', dimensions=['Slickness', 'Awesomeness'])
profile1.save()
profile2 = models.RatingProfile(title='Profile 2', dimensions=['Efficiency', 'Enthusiasm', 'Sarcasm'])
profile2.save()
profile3 = models.RatingProfile(title='Profile 3', dimensions=['Slipperiness', 'Surliness'])
profile3.save()

# Make a few Employees.
master = models.Employee(first_name='Master',
                         last_name='Trash',
                         rating_profile=profile1,
                         business=business,
                         bio='The master of trash.')
master.save()
mystical = models.Employee(first_name='Mystical',
                           last_name='Beast',
                           rating_profile=profile1,
                           business=business,
                           bio='foo')
mystical.save()
luke = models.Employee(first_name='Infinite',
                       last_name='Luke',
                       rating_profile=profile2,
                       business=business2,
                       bio='StackOverflowError at populate.py, line 60')
luke.save()

# Make some Ratings.
rating1 = models.Rating(title='Awesomeness', rating_value=5, employee=master, id=1)
rating1.save()
rating2 = models.Rating(title='Slickness', rating_value=5, employee=mystical)
rating2.save()
rating3 = models.Rating(title='Efficiency', rating_value=1, employee=mystical)
rating3.save()
rating4 = models.Rating(title='Surliness', rating_value=4, employee=master)
rating4.save()

# Make a couple of NewsFeedItems.
nfi1 = models.NewsFeedItem(title='Apatapa arrives in Tahoe!',
                           subtitle='proceed to code',
                           body='After an insane amout of driving, we finally got there.',
                           date=datetime.datetime.now(),
                           date_edited=datetime.datetime.now(),
                           business=business)

nfi1.save()
nfi2 = models.NewsFeedItem(title='Foo!',
                           subtitle='Bar?',
                           body='Baz.',
                           date=datetime.datetime.now(),
                           date_edited=datetime.datetime.now(),
                           business=business)
nfi2.save()
nfi3 = models.NewsFeedItem(title='Try our new parrots!',
                           subtitle='Delicious, nutritious.',
                           body='These parrots are selling for a dollar.',
                           date=datetime.datetime.now(),
                           date_edited=datetime.datetime.now(),
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
q2 = models.Question(label='Yes or no?', type='CG', options=['yes', 'no'], survey=s1)
q2.save()
q3 = models.Question(label='What is your favorite color?', type='TF', options=['blue', 'yellow', 'aaargh!'], survey=s1)
q3.save()
q4 = models.Question(label='Tell us your life story', type='TA', survey=s1)
q4.save()

# Write responses.
qr1 = models.QuestionResponse(question=q1, response=['yes'])
qr1.save()
qr2 = models.QuestionResponse(question=q2, response=['no'])
qr2.save()
qr3 = models.QuestionResponse(question=q3, response=['aaargh!'])
qr3.save()
qr4 = models.QuestionResponse(question=q4, response=['Life story HERE.'])
qr4.save()

print 'apatapa!'

#!/usr/bin/env python

from datetime import datetime, timedelta
from django.utils.timezone import utc

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'applaud.settings')

import applaud.settings
from applaud import models
from django.contrib.auth.models import User, Group
from random import random
from applaud import business_views
from applaud import settings
import Image

# Make a User.
user = User.objects.create_user('Boo Furgers', 'boofurgers@aol.com', 'applaud')
user2 = User.objects.create_user('Apatapa', 'alsdafasdf@gmail.com', 'applaud')
enduser = User.objects.create_user('little keith', 'mastertrash@gmail.com', 'apatapa')
enduser.first_name="Keith"
enduser.last_name="Cox"
enduser.save()
# Make another user.
enduser2 = User.objects.create_user('john harris', 'mamabear@berensteinbears.com', 'apatapa')
enduser2.first_name="John"
enduser2.last_name="Harris"
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
                                        goog_id='23l;asdr4ajiaf', business_name="Pacific Catch")


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

# Get the user to follow the business.
userprofile.businesses_followed.add(business, keith_business)
userprofile2.businesses_followed.add(business, keith_business)
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
friendlinessw = models.RatedDimension(title='Friendliness',
                                      rating_profile=keith_waiter_profile)
friendlinessw.save()
helpfulnessw = models.RatedDimension(title='Helpfulness',
                                     rating_profile=keith_waiter_profile)
helpfulnessw.save()

keith_hostess_profile = models.RatingProfile(title='Hostess', business=keith_business)
keith_hostess_profile.save()
friendlinessh = models.RatedDimension(title='Friendliness',
                                      rating_profile=keith_hostess_profile)
friendlinessh.save()
helpfulnessh = models.RatedDimension(title='Helpfulness',
                                     rating_profile=keith_hostess_profile)
helpfulnessh.save()
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
# master = models.EmployeeProfile(business=business,
#                                 user=emp_user,
#                                 rating_profile=profile2,
#                                 bio='foo')
# master.save()
# mystical = models.EmployeeProfile(business=business2,
#                                   user=emp_user2,
#                                   rating_profile=profile2,
#                                   bio='bio')
# mystical.save()
# mystical2 = models.EmployeeProfile(business=business,
#                                   user=emp_user3,
#                                   rating_profile=profile3,
#                                   bio='bio')
# mystical2.save()
# luke = models.EmployeeProfile(business=business2,
#                               user=emp_enduser,
#                               rating_profile=profile3,
#                               bio='biology')
# luke.save()

# mystical2 = models.EmployeeProfile(business=business,
#                                   user=emp_user6,
#                                   rating_profile=profile1,
#                                   bio="Super super bio!!!!!")
# mystical2.save()

# mystical2 = models.EmployeeProfile(business=business,
#                                   user=emp_user4,
#                                   rating_profile=profile1,
#                                   bio='The bioiest of all bioed bios')
# mystical2.save()

# mystical2 = models.EmployeeProfile(business=business,
#                                   user=emp_user5,
#                                   rating_profile=profile3,
#                                   bio="Another lovely bio for another employee of the month! Ring the bell, hit the gong, we\'ve got a superstar on our hands! Remember back when you were just a kid??")
# mystical2.save()

moe = models.EmployeeProfile(business=keith_business,
                             user=emp_user,
                             rating_profile=keith_waiter_profile,
                             bio='I grew up in South San Francisco, went to Cal, and began working at Pacific Catch in 2010. I hope to get my master\'s and work in restaurant management.')
moe.save()
jill = models.EmployeeProfile(business=keith_business,
                              user=emp_user2,
                              rating_profile=keith_hostess_profile,
                              bio='I am from Denmark. I currently go to art school and am studying portraiture.')
jill.save()
jeremy = models.EmployeeProfile(business=keith_business,
                                user=emp_user3,
                                rating_profile=keith_waiter_profile,
                                bio='After graduating from Oberlin College in 1993, I tried my hand at microbrewing, but found it much too small. I am our oldest employee, and dream of owning my own restaurant.')
jeremy.save()
josh = models.EmployeeProfile(business=keith_business,
                              user=emp_enduser,
                              rating_profile=keith_waiter_profile,
                              bio='Hailing from Sydney, Australia, I moved to California to experience the American lifestyle. In my free time, I love to sample the surfing sights.')
josh.save()

jordan = models.EmployeeProfile(business=keith_business,
                                user=emp_user6,
                                rating_profile=keith_waiter_profile,
                                bio='Pacific Catch is the 10th restaurant I have waitressed in and it is by far the best.  I have lived in 13 states and California is definitely home for good.')
jordan.save()

jack = models.EmployeeProfile(business=keith_business,
                              user=emp_user4,
                              rating_profile=keith_hostess_profile,
                              bio='I am an avid extreme sportsman and chef. My favorite place to play is Lake Tahoe.')
jack.save()

sarah = models.EmployeeProfile(business=keith_business,
                               user=emp_user5,
                               rating_profile=keith_waiter_profile,
                               bio='I grew up in Mill Valley and I hope to never leave. I would love to start my own chocolate studio.')
sarah.save()

# Make some Ratings. Only "master" has ratings.
# 'master' can be rated on 'awesomeness' and 'slickness'
quality_dim = profile1.rateddimension_set.get(title='Quality')
for i in range(10):
    today = datetime.utcnow().replace(tzinfo=utc)+timedelta(days=i)
    print today
    rating1 = models.Rating(title='Friendliness',
                            rating_value=5*random(),
                            employee=moe,
#                            id=1,
                            date_created=today,
                            dimension=friendlinessw,
                            user=userprofile)
    rating1.save()
    rating2 = models.Rating(title='Promptness',
                            rating_value=5*random(),
                            employee=jeremy,
                            date_created=today,
                            dimension=promptness,
                            user=userprofile)
    rating2.save()
    rating3 = models.Rating(title='Quality',
                            rating_value=5*random(),
                            employee=jill,
                            date_created=today,
                            dimension=quality_dim,
                            user=userprofile)
    rating3 = models.Rating(title='Quality',
                            rating_value=5*random(),
                            employee=jill,
                            date_created=today,
                            dimension=quality_dim,
                            user=userprofile)
    rating3.save()

# Make a couple of NewsFeedItems.
nfi1 = models.NewsFeedItem(title='Pacific Catch Opens Fourth Location In South Bay',
                           subtitle='in Campbell, CA',
                           body='We have recently opened our fourth location, in Campbell. Expect to see our innovative flavors featured on the menu every night!',
                           date=datetime.utcnow().replace(tzinfo=utc),
                           date_edited=datetime.utcnow().replace(tzinfo=utc),
                           business=keith_business)

nfi1.save()
nfi2 = models.NewsFeedItem(title='Featured Chef Chandon Clenard on CleanFish.com ',
                           subtitle='committed to a more sustainable future',
                           body='Chef Chandon believes that a healthy environment is the most important part of Pacific Catch.',
                           date=datetime.utcnow().replace(tzinfo=utc),
                           date_edited=datetime.utcnow().replace(tzinfo=utc),
                           business=keith_business)
nfi2.save()
nfi3 = models.NewsFeedItem(title='Pacific Catch on Apatapa!',
                           subtitle='check us out on your iPhone',
                           body='We hope that using Apatapa will allow us to give our customers a better experience.',
                           date=datetime.utcnow().replace(tzinfo=utc),
                           date_edited=datetime.utcnow().replace(tzinfo=utc),
                           business=keith_business)
nfi3.save()

# Make Surveys.
s1 = models.Survey(title='Emacs?', description='Text editor of the gods.', business=business)
s1.save()
s2 = models.Survey(title='Apatapa?', description='Apps providing apatapa through apps providing apatapa', business=business2)
s2.save()
s3 = models.Survey(title='Feedback', description='We want your help improving Pacific Catch.', business=keith_business)
s3.save()

# Make Questions.
q1 = models.Question(label='Would you join us for live jazz on Thursday nights?', type='RG', options=['yes', 'no'], survey=s3)
q1.save()
q2 = models.Question(label='Are these good locations for the next Pacific Catch?', type='CG', options=['Burlingame', 'Orinda', 'Lucas Valley'], survey=s3)
q2.save()
q3 = models.Question(label='What do you wish we served?', type='TF', options=[], survey=s3)
q3.save()
q4 = models.Question(label='Tell us your favorite Pacific Catch story.', type='TA', survey=s3)
q4.save()

# Write responses.
# qr1 = models.QuestionResponse(question=q1,
#                               response=['yes'],
#                               date_created=datetime.utcnow().replace(tzinfo=utc),
#                               user=userprofile)
# qr1.save()

for i in range(10):
    today = datetime.utcnow().replace(tzinfo=utc)+timedelta(days=i)
    options = ["yes","no"]
    profiles = [userprofile,userprofile2]
    which = options[int(2*random())]
    qr2 = models.QuestionResponse(question=q1,
                                  response=[which],
                                  date_created=today,
                                  user=profiles[int(random()*2)])
    qr2.save()

qr3 = models.QuestionResponse(question=q3,
                              response=['Ahi tuna'],
                              date_created=datetime.utcnow().replace(tzinfo=utc),
                              user=userprofile)
qr3.save()
qr4 = models.QuestionResponse(question=q4,
                              response=['I came to Pacific Catch on my birthday with my family, and had a great time!'],
                              date_created=datetime.utcnow().replace(tzinfo=utc),
                              user=userprofile2)
qr4.save()

keith_photo = models.BusinessPhoto(business=keith_business,
                                   tags=['tag', 'tagged', 'mystical'],
                                   uploaded_by=userprofile)
keith_photo.save()
business_views.save_image(keith_photo.image,
                          'keith_photo_test.jpg',
                          settings.MEDIA_ROOT + 'noimage.png')

keith_photo2 = models.BusinessPhoto(business=keith_business,
                                   tags=['foo', 'bar'],
                                   uploaded_by=userprofile2)
business_views.save_image(keith_photo2.image,
                          'keith_photo_numero_dos.jpg',
                          settings.MEDIA_ROOT + 'noimage.png')

# some messages and inbox items
inbox1 = models.Inbox(user=keith_business.user)
inbox1.save()
inbox2 = models.Inbox(user=userprofile2.user)
inbox2.save()
inbox3 = models.Inbox(user=userprofile.user)
inbox3.save()
message1 = models.MessageItem(text='Welcome to the Apatapa family! Also your sandwich was god awful',
                              date_created=datetime.utcnow().replace(tzinfo=utc),
                              inbox = inbox1,
                              subject='sandwich',
                              sender = userprofile2.user)
message1.save()

message2 = models.MessageItem(text='I am fucking tired of finding roaches in my sandwiches!!!!',
                              date_created=datetime.utcnow().replace(tzinfo=utc),
                              inbox = inbox1,
                              subject='',
                              sender = userprofile2.user)

message2.save()
print 'apatapa!'

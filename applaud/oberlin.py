#!/usr/bin/env python

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'applaud.settings')

from applaud import settings
import applaud.settings
from applaud import models
from django.contrib.auth.models import User, Group

with open('apatapa_places.txt') as f:
    for line in f:

        line = line.strip()
        parts = line.split(',')
        
        name = parts[0]
        lat = float(parts[1])
        lon = float(parts[2])

        user = User.objects.create_user(name, 'apatapa@apatapa.com', 'applaud')
        
        business = models.BusinessProfile(user=user, phone='', latitude=lat, longitude=lon, goog_id='', business_name=name, isApplaud=0, isNewsfeed=0, isPolls=0)
        business.save()
        
        # Hash to get the fake google id?
        # In the meantime just use the pk

        biz_id = business.id
        business.goog_id = biz_id
        business.save()

# For the businesses in town
with open('apatapa_businesses.txt') as f:
    for line in f:

        line = line.strip()
        parts = line.split(',')
        
        name = parts[0]
        lat = float(parts[1])
        lon = float(parts[2])

        user = User.objects.create_user(name, 'apatapa@apatapa.com', 'applaud')
        
        business = models.BusinessProfile(user=user, phone='', latitude=lat, longitude=lon, goog_id='', business_name=name, isApplaud=0)
        business.save()
        
        # Hash to get the fake google id?
        # In the meantime just use the pk

        biz_id = business.id
        business.goog_id = biz_id
        business.save()

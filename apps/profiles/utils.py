from django.conf import settings
from django.db.models import Avg, Max, Min, Count, StdDev, F
from django.contrib.auth.models import User

# Python standard
import math
from datetime import date as _date
# Theproject
from profiles.models import UserProfile
# External
from notification import models as notification





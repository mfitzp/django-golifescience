import os.path
import datetime
# Django
from django.conf import settings
from django.db import models
from django.contrib.comments.signals import comment_was_posted
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse


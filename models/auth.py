from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from .config import AccountSettings 

class SystemAccount(models.Model):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length = 200,
        help_text = 'Name of business')
    password = models.CharField(max_length = 300)
    email = models.EmailField(help_text = '''Used to login 
        as administrator.''')
    settings = models.OneToOneField(AccountSettings,
    	models.CASCADE)
    initial_setup_done = models.BooleanField(default = False)
    created = models.DateTimeField(auto_now_add = True)

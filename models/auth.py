from django.contrib.auth.models import AbstractUser
from django.db import models
from .config import AccountSettings 

class SystemUser(AbstractUser):
	account = models.ForeignKey('SystemAccount', models.CASCADE, null = True)
	is_admin = models.BooleanField(default = False)

class SystemAccount(models.Model):
    name = models.CharField(max_length = 200,
        help_text = 'Name of business')
    password = models.CharField(max_length = 300)
    email = models.EmailField(help_text = '''Used to login 
        as administrator.''')
    settings = models.OneToOneField(AccountSettings,
    	models.CASCADE)
    created = models.DateTimeField(auto_now_add = True)

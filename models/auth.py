from django.contrib.auth.models import AbstractUser
from django.db import models
from .config import SystemAccount 

class SystemUser(AbstractUser):
	account = models.ForeignKey('SystemAccount', models.CASCADE, null = True)

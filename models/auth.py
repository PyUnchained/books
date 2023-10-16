from functools import cached_property

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class SystemAccount(models.Model):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length = 200)
    email = models.EmailField(help_text = '''Used for reporting 
        and data recovery.''', blank = True, null = True)
    settings = models.OneToOneField("books.AccountSettings", models.CASCADE, null = True,
        blank = True)
    initial_setup_done = models.BooleanField(default = False)
    created = models.DateTimeField(auto_now_add = True)

    def __str__(self, *args, **kwargs):
        return self.name

    @cached_property
    def Account(self):
        from books.models.accounts import Account
        return Account

    def get_account(self, **account_kwargs):
        account_kwargs.update({'system_account':self})
        return self.Account.objects.get(**account_kwargs)

    def create_subaccount(self, parent, name = None, code_suffix = None, **account_kwargs):

        if not name or not code_suffix:
            raise ValueError('Following kwargs are required: name, code_suffix.')

        acc_code = parent.code + f" - {code_suffix}"
        account_kwargs.update({'system_account':self, 'code':acc_code, 'parent':parent,
            'name': name})
        new_account, created = self.Account.objects.get_or_create(**account_kwargs)
        return new_account

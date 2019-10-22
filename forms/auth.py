from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, MultiField, HTML

from books.models.config import SystemAccount

class AccountRegistrationForm(forms.ModelForm):
	confirm_password = forms.CharField(max_length = 200)
	class Meta():
		model = SystemAccount
		fields = ['name', 'password', 'confirm_password', 'email']

	def clean(self, *args, **kwargs):
		cleaned_data = super().clean(*args, **kwargs)
		if cleaned_data['confirm_password'] != cleaned_data['password']:
			raise ValidationError('Passwords did not match!')

from django import forms

class RequestUserSystemAccountAdminFormMixin():

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields['system_account'].widget = forms.HiddenInput()
        except KeyError:
            pass

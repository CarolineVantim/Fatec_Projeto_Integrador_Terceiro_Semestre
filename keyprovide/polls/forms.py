from django.core.exceptions import ValidationError
from polls.models import User
from django import forms

'''
class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['fullname', 'birthday', 'nationality', 'password']
        error_messages = {
            'fullname': {
                'required': ("Informe o nome completo."),
            },
            'birthday': {
                'required': ("Informe uma data válida."),
            },
            'nationality': {
                'required': ("Informe a naturalidade."),
            },
            'password': {
                'required': ("Informe uma senha válida."),
            },
            'confirm_password': {
                'required': ("É necessário confirmar a senha."),
            }
        }

    def clean(self):
        self.cleaned_data = super().clean()
        return self.cleaned_data
'''

class UserForm(forms.Form):
    first_name = forms.CharField(label="firstname", max_length=100)
    last_name = forms.CharField(label="lastname", max_length=100)
    #fullname = forms.CharField(label= "fullname", max_length=100)
    username = forms.CharField(label= "username", max_length=100)
    email = forms.CharField(label= "email", max_length=50)
    #birthday = forms.CharField(label= "birthday", max_length=50)
    #nationality = forms.CharField(label= "nationality", max_length=50)
    password = forms.CharField(label= "password", max_length=50, widget=forms.PasswordInput())
    confirm_password = forms.CharField(label= "confirm_password", max_length=50)
    
    def clean_username(self):
        username = self.cleaned_data['username']
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        words = [w.capitalize() for w in first_name.split()]
        return ' '.join(words)

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        words = [w.capitalize() for w in last_name.split()]
        return ' '.join(words)

    def clean_password(self):
        password = self.cleaned_data['password']
        return password

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data['confirm_password']
        return confirm_password

    def clean_email(self):
        email = self.cleaned_data['email']
        return email
'''
    def clean(self):
        self.cleaned_data = super().clean()
        return self.cleaned_data
'''
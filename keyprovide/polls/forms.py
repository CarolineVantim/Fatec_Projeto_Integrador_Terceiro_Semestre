from django import forms

class UserForm(forms.Form):
    email = forms.CharField(label= "email", max_length=50)
    password = forms.CharField(label= "password", max_length=50, widget=forms.PasswordInput())
    confirm_password = forms.CharField(label= "confirm_password", max_length=50, widget=forms.PasswordInput())
    name = forms.CharField(label="name", max_length=100)
    cnpj = forms.CharField(label="cnpj", max_length=14, required=False)
    cep = forms.CharField(label="cep", max_length=9)
    number = forms.IntegerField(label="number")
    block = forms.CharField(label="block", max_length=100)
    city = forms.CharField(label="city", max_length=100)
    state = forms.CharField(label="state", max_length=20)
    is_juridic = forms.BooleanField(label="is_juridic")

    def clean_password(self):
        password = self.cleaned_data['password']
        return password
    
    def clean_confirm_password(self):
        confirm_password = self.cleaned_data['confirm_password']
        return confirm_password
    
    def clean_email(self):
        email = self.cleaned_data['email']
        return email

    def clean(self):
        self.cleaned_data = super().clean()
        return self.cleaned_data

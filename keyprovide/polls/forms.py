from django import forms

class UserForm(forms.Form):
    email = forms.CharField(label= "Email", max_length=50)
    email.widget = forms.TextInput(attrs={'class': 'form-control'})
    password = forms.CharField(label= "Senha", max_length=50, widget=forms.PasswordInput())
    password.widget = forms.TextInput(attrs={'class': 'form-control', 'type': 'password'})
    confirm_password = forms.CharField(label= "Confirme sua senha", max_length=50)
    confirm_password.widget = forms.TextInput(attrs={'class': 'form-control', 'type': 'password'})
    name = forms.CharField(label="Nome", max_length=100)
    name.widget = forms.TextInput(attrs={'class': 'form-control'})
    cnpj = forms.CharField(label="CNPJ", max_length=14)
    cnpj.widget = forms.TextInput(attrs={'class': 'form-control'})
    cep = forms.CharField(label="CEP", max_length=9)
    cep.widget = forms.TextInput(attrs={'class': 'form-control'})
    num = forms.IntegerField(label="Numero")
    num.widget = forms.TextInput(attrs={'class': 'form-control'})
    bairro = forms.CharField(label="Bairro", max_length=100)
    bairro.widget = forms.TextInput(attrs={'class': 'form-control'})
    cidade = forms.CharField(label="Cidade", max_length=100)
    cidade.widget = forms.TextInput(attrs={'class': 'form-control'})
    estado = forms.CharField(label="Estado", max_length=2)
    estado.widget = forms.TextInput(attrs={'class': 'form-control'})
    is_juridico = forms.BooleanField()

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
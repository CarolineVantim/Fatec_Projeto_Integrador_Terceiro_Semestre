from djongo import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class MarketPlaceProducts(models.Model):
    meta_keywords = models.CharField('meta_keywords', max_length=300)
    name = models.CharField('name', max_length=200)
    description = models.CharField('description', max_length=600)
    category = models.CharField('category', max_length=200)
    attributes = models.CharField('attributes', max_length=200)
    image = models.CharField('image', max_length=100)
    reference = models.CharField('reference', max_length=200)
    product_link = models.CharField('product_link', max_length=100)
    expired_date = models.CharField('expired_date', max_length=10)
    price_from = models.FloatField('price_from')
    price_to = models.FloatField('price_to')
    marketplace = models.CharField('marketplace', max_length=200)
    persuasive_text = models.CharField('persuasive_text', max_length=500, null=True)
    updated_at = models.DateTimeField(
        verbose_name='Updated At',
        auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.description


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O Email deve ser informado')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    email = models.EmailField(unique=True, max_length=254)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    name = models.CharField('name', max_length=100, default="Não informado")
    cnpj = models.CharField('cnpj', max_length=14, blank=True)
    cep = models.CharField('cep', max_length=9, default="000000-000")
    number = models.IntegerField('number', default=000)
    block = models.CharField('block', max_length=100, default="Não informado")
    city = models.CharField('city', max_length=100, default="Não informado")
    state = models.CharField('state', max_length=2, default="NA")
    is_juridic = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    
    objects = UserManager()
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_perms(self, perm_list, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_staff

class DonationList(models.Model):
    user_id  =  models.IntegerField()
    reference = models.CharField('reference', max_length=200)
    was_donated = models.BooleanField(default=False)
    donated_by = models.IntegerField(null=True)
    quantaty = models.IntegerField()
    list_control_id = models.IntegerField(default=0)
    
    def __str__(self):
        return self.description

class DonationListControl(models.Model):
    user_id  =  models.IntegerField()
    closed = models.CharField(default='False', max_length=6)
    create_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(
        verbose_name='Updated At',
        auto_now_add=False, auto_now=True)

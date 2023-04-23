from django.db import models


class GoodAfter(models.Model):
    meta_keywords = models.CharField('meta_keywords', max_length=300)
    name = models.CharField('name', max_length=200)
    description = models.CharField('description', max_length=600)
    category = models.CharField('category', max_length=200)
    attributes = models.CharField('attributes', max_length=200)
    image = models.CharField('image', max_length=100)
    reference = models.CharField('reference', max_length=200)
    product_link = models.CharField('product_link', max_length=100)
    expired_date = models.CharField('expired_date', max_length=10)
    updated_at = models.DateTimeField(
        verbose_name='Updated At',
        auto_now_add=False, auto_now=True)

    def __str__(self):
        return self.description


class User(models.Model):
    fullname = models.CharField('name', max_length=200)
    birthday = models.PositiveIntegerField('birthday', default=0, null=True)
    nationality = models.CharField('nationality', max_length=200)
    username = models.CharField('username', max_length=200)
    email = models.CharField('email', max_length=100)
    password = models.CharField('password', max_length=100)

    def __str__(self):
        return self.fullname
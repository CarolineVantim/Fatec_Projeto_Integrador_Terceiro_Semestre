from django.contrib import admin
from .models import MarketPlaceProducts
from .models import User
from .models import DonationList


admin.site.register(MarketPlaceProducts)
admin.site.register(User)
admin.site.register(DonationList)

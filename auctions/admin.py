from django.contrib import admin
from .models import Category, AuctionListing

# Register your models here.
admin.site.register(Category)

admin.site.register(AuctionListing)
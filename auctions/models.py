from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
# from django.conf import settings


class User(AbstractUser):
    pass


# Implement model for the item categories
class Category(models.Model):
    category_name = models.CharField(max_length=64, blank=False)

    # When this category is displayed as a string, select what it will show up as on the site
    def __str__(self):
        return self.category_name


# Implement model for the Auction Listings
class AuctionListing(models.Model):
    name = models.CharField(max_length=128, blank=False)  # Name of the listing is a CharField, max length allowed 128 characters
    description = models.TextField(blank=False)  # Item description is a text field with undefined length for now
    starting_bid = models.DecimalField(max_digits=8, decimal_places=2, blank=False)  # Starting bid with 2dp, up to 1 Million
    current_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)  # Current price, same as above
    image_link = models.URLField(blank=True)  # Optional field for image link URL
    category = models.CharField(max_length=128, blank=True, null=True)  # Category will be its own class so that admin users can add mroe categories if needed

    # When this listing is displayed on the site, show the name as a default
    def __str__(self):
        return self.name

    #
    def get_absolute_url(self):
        return reverse('index')

#
# # Implement model for bids
# class Bids(models.Model):
#     #bidder = settings.AUTH_USER_MODEL  # Get the name of the user making a new bid
#     bid = models.DecimalField(max_digits=8, decimal_places=2, blank=False)  # Store the value of the new bid
#     listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="auction_listing")


# # Implement model for comments
# class Comments(models.Model):
#     commentor = User.get_username()  # Get the name of the user creating the comment
#     listing = models.OneToOneField(AuctionListing, on_delete=models.CASCADE)
#
#
# # Implement model for each user's watchlist
# class Watchlist(models.Model):
#     user = User.get_username()  # Get the name of the user who's Watchlist we are going to
#     listings = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="listing")

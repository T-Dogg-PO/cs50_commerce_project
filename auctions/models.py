from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.conf import settings


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
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=False)  # Starting bid with 2dp, up to 1 Million
    current_highest_bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name="current_highest_bidder") # For storing the user who has the highest bid currently
    image_link = models.URLField(blank=True)  # Optional field for image link URL
    category = models.CharField(max_length=128, blank=True, null=True)  # Category will be its own class so that admin users can add mroe categories if needed
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1) # The user who creates and owns this listing
    active = models.BooleanField(default=True) # Boolean field to show if this listing is active or not
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name="winner") # For storing who wins the auction once it closes

    # When this listing is displayed on the site, show the name as a default
    def __str__(self):
        return self.name

    # Gives a direct link to view on site when editing these listings in the admin panel. If anyone has a better description for what this does, please let me know! I am a bit confused.
    def get_absolute_url(self):
        return reverse('')


# Implement model for bids
class Bid(models.Model):
    bidder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1) # Get the name of the user making a new bid
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, default=1) # Link to the listing table
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=False) # Store the value of the new bid

    def __str__(self):
        return '%s - %s' % (self.listing.name, self.price)


# Implement model for comments
class Comment(models.Model):
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments") # Link to the listing table
    commentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1) # Get the name of the user creating the comment
    content = models.TextField(blank=False) # The body of the comment
    date_added = models.DateTimeField(auto_now_add=True) # The date and time of the comment creation

    def __str__(self):
        return '%s - %s' % (self.listing.name, self.commentor)


# Implement model for each user's watchlist
class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1) # Get the name of the user who has this watchlist
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, default=1) # Get each listing which is added to the watchlist

    def __str__(self):
        return f"{self.user}'s watchlist"

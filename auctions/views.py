from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH
from django.contrib import messages

from .models import User, AuctionListing, Category, Bid, Comment, Watchlist

# Create our category choices variable based on the categories that get created in the Admin view
category_choices = Category.objects.all().values_list('category_name', 'category_name')
category_choices_list = []
for item in category_choices:
    category_choices_list.append(item)


# Create Django Form for creating a new listing
class Create(forms.ModelForm):
    class Meta:
        # Take fields from the AuctionListing model
        model = AuctionListing
        # For this form, display only these fields
        fields = ['name', 'description', 'price', 'image_link', 'category']
        # Use default input types for all the fields (defined in models.py), but specify that categories will be
        # selected from the list of available categories
        widgets = {
            'category': forms.Select(choices=BLANK_CHOICE_DASH + category_choices_list)
        }


# Create Django Form for adding a new bid to a listing
class Bid_Form(forms.ModelForm):
    class Meta:
        # Take fields from Bid model
        model = Bid
        # For this form, display only the price field
        fields = ['price']

# Django form for creating a new comment
class Comment_Form(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


# Default view / landing page
def index(request):
    return render(request, "auctions/index.html", {
        "active_listings": AuctionListing.objects.filter(active=True)
    })


# Method for creating new listings
def create(request):
    # If request type is POST (i.e. the form is being submitted from the Create page), then store the submitted data
    # in create_form
    if request.method == "POST":
        create_form = Create(request.POST)

        # If the form is valid, create an empty row in AuctionListing and fill each applicable section from the
        # cleaned data
        if create_form.is_valid():
            new_listing = AuctionListing()
            new_listing.name = create_form.cleaned_data["name"]
            new_listing.description = create_form.cleaned_data["description"]
            new_listing.price = create_form.cleaned_data["price"]
            new_listing.image_link = create_form.cleaned_data["image_link"]
            new_listing.category = create_form.cleaned_data["category"]
            new_listing.user = request.user

            new_listing.save()

            return redirect('index')

        return redirect('index')

    # Otherwise, return the create new listing form
    else:
        return render(request, "auctions/create.html", {
            "create_form": Create()
        })


# Method for viewing a listing's details
def listing(request, listing_id):
    # Get the listing in question from the database
    current_listing = AuctionListing.objects.get(id=listing_id)

    # Perform checks to see if this listing is active or not. If a user who is not the owner or winner of a closed auction tries to access
    # the page (e.g. through a direct link), display an error instead
    if current_listing.winner is not None:
        if current_listing.active == False and request.user.id != current_listing.winner.id and request.user.id != current_listing.user.id:
            return render(request, "auctions/error.html", {
                "error": "This auction is no longer active"
            })
    else:
        if current_listing.active == False and request.user.id != current_listing.user.id:
            return render(request, "auctions/error.html", {
                "error": "This auction is no longer active"
            })

    # Check if the user is authenticated and if the listing exists on their watchlist. Display HTML differently depending
    # on watchlist options
    if request.user.is_authenticated:
        if Watchlist.objects.filter(user=request.user, listing=listing_id).exists():
            return render(request, "auctions/listing.html", {
                "listing": current_listing,
                "place_bid": Bid_Form(),
                "new_comment": Comment_Form(),
                "watchlist": True,
            })
    else:
        return render(request, "auctions/listing.html", {
            "listing": current_listing,
            "place_bid": Bid_Form(),
            "new_comment": Comment_Form(),
            "watchlist": False,
        })

    return render(request, "auctions/listing.html", {
        "listing": current_listing,
        "place_bid": Bid_Form(),
        "new_comment": Comment_Form(),
        "watchlist": False,
    })


# Method for showing all the listings a user has created
def my_listings(request):
    if AuctionListing.objects.filter(user=request.user).exists():
        return render(request, "auctions/my_listings.html", {
            "my_listings": AuctionListing.objects.filter(user=request.user)
        })

    return render(request, "auctions/my_listings.html", {
        "my_listings": None
    })

# Method for placing a new bid on a current listing
def new_bid(request, listing_id):
    # If method is post, store the submitted data in bid_form
    if request.method == "POST":
        bid_form = Bid_Form(request.POST)

        # Check if the form is valid
        if bid_form.is_valid():
            # Get information about the listing in question and the sumbitted new bid
            current_listing = AuctionListing.objects.get(id=listing_id)
            current_price = current_listing.price

            bid_price = bid_form.cleaned_data["price"]

            # Validate that the new bid is higher than the old price
            if bid_price <= current_price:
                messages.error(request, 'Error: New bid must be higher than the current highest bid')
                return redirect('listing', listing_id)
            # If yes, save all the data to the database and return to the listing page
            else:
                bid = Bid()
                bid.listing = current_listing
                bid.price = bid_price
                current_listing.price = bid_price
                current_listing.current_highest_bidder = request.user
                current_listing.save()
                bid.save()
                return HttpResponseRedirect(reverse('listing', args=[listing_id]))
        return index(request)
    return index(request)


# Method for creating a new comment on a listing
@login_required
def new_comment(request, listing_id):
    # If method is post, store submitted data in comment_form
    if request.method == "POST":
        comment_form = Comment_Form(request.POST)

        # If data is valid, save all the comment details in a Comment model
        if comment_form.is_valid():
            current_listing = AuctionListing.objects.get(id=listing_id)
            comment = Comment()
            comment.listing = current_listing
            comment.content = comment_form.cleaned_data["content"]
            comment.commentor = request.user
            comment.save()

            # Return to the listing page
            return listing(request, listing_id)

    return listing(request, listing_id)


# Method for listing the categories
def categories(request):
    current_categories = []
    for category in category_choices_list:
        current_categories.append(category[1])

    return render(request, "auctions/categories.html", {
        "cats": current_categories
    })


# Method for displaying all of the listings under a specific category
def category(request, cat):
    return render(request, "auctions/category.html", {
        "category": cat,
        "list_of_listings": AuctionListing.objects.filter(category=cat)
    })


# Method for viewing a users watchlist
@login_required
def watchlist(request):
    # Check for Watchlist objects to exist for a user, and check that they are still active
    if Watchlist.objects.filter(user=request.user, listing__active=True).exists():
        return render(request, "auctions/watchlist.html", {
            "watchlist": Watchlist.objects.filter(user=request.user, listing__active=True)
        })

    return render(request, "auctions/watchlist.html", {
        "watchlist": None
    })

# Method for adding a listing to a users watchlist
@login_required
def watchlist_add(request, listing_id):
    current_listing = AuctionListing.objects.get(id=listing_id)

    watchlist_item = Watchlist()
    watchlist_item.user = request.user
    watchlist_item.listing = current_listing
    watchlist_item.save()

    return listing(request, listing_id)


# Method for removing a listing from a users watchlist
@login_required
def watchlist_remove(request, listing_id):
    current_listing = AuctionListing.objects.get(id=listing_id)

    watchlist_item = Watchlist.objects.get(listing=current_listing)
    watchlist_item.delete()
    return listing(request, listing_id)


# Method for declaring a winner
@login_required
def winner(request, listing_id):
    current_listing = AuctionListing.objects.get(id=listing_id)

    current_listing.active = False
    current_listing.winner = current_listing.current_highest_bidder
    current_listing.save()

    return listing(request, listing_id)


# Method for seeing auctions that you have won
@login_required
def winnings(request):
    if AuctionListing.objects.filter(winner=request.user).exists():
        return render(request, "auctions/winnings.html", {
            "winnings": AuctionListing.objects.filter(winner=request.user)
        })

    return render(request, "auctions/winnings.html", {
        "winnings": None
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH

from .models import User, AuctionListing, Category

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
        fields = ['name', 'description', 'starting_bid', 'image_link', 'category']
        # Use default input types for all the fields (defined in models.py), but specify that categories will be
        # selected from the list of available categories
        widgets = {
            'category': forms.Select(choices=BLANK_CHOICE_DASH + category_choices_list)
        }


# Default view / landing page
def index(request):
    return render(request, "auctions/index.html", {
        "active_listings": AuctionListing.objects.all()
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
            new_listing.starting_bid = create_form.cleaned_data["starting_bid"]
            new_listing.image_link = create_form.cleaned_data["image_link"]
            new_listing.category = create_form.cleaned_data["category"]

            new_listing.save()

            return redirect('index')

        return redirect('index')

    else:
        return render(request, "auctions/create.html", {
            "create_form": Create()
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

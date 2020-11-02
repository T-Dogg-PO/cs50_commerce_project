from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("new_bid/<int:listing_id>", views.new_bid, name="new_bid"),
    path("new_comment/<int:listing_id>", views.new_comment, name="new_comment"),
    path("categories", views.categories, name="categories"),
    path("category/<str:cat>", views.category, name="category"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist_add/<int:listing_id>", views.watchlist_add, name="watchlist_add"),
    path("watchlist_remove/<int:listing_id>", views.watchlist_remove, name="watchlist_remove"),
    path("winner/<int:listing_id>", views.winner, name="winner"),
    path("winnings", views.winnings, name="winnings"),
    path("my_listings", views.my_listings, name="my_listings")
]

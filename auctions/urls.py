from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("showproduct/<str:title>", views.showproduct, name="showproduct"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("add_to_watchlist/<str:title>", views.add_to_watchlist, name="add_to_watchlist"),
    path("remove_from_watchlist/<str:title>", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("edit/<str:title>", views.edit, name="edit"),
    path("bid/<str:title>", views.bid, name="bid"),
    path("close/<str:title>", views.close, name="close"),
    path("close/<str:title>", views.close, name="close"),
    path("comment/<str:title>", views.comment, name="comment"),
    path("categories", views.categories, name="categories"),
    path("show_ctg/<str:category>", views.show_ctg, name="show_ctg"),
    
]

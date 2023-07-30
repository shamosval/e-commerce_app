from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Max

from .models import *



def index(request):
    # Get active listings and reverse them so that most recently added listing is shown on top
    products = Product.objects.filter(active=True)
    # products = Product.objects.all()

    reversed_products = sorted(products, key=lambda x: x.id, reverse=True)
    return render(request, "auctions/index.html", {'products': reversed_products})


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

somebody_bid = False

@login_required
def create(request):
    categories = Category.objects.all()

    if request.method == "POST":
        
        name = request.POST["name"]
        description = request.POST["description"]
        price = request.POST["price"]
        cat_id = request.POST.get('category')
        

        if not cat_id:
            category = request.POST.get('new_category')
            new_category = Category(category=category)
            new_category.save()
            category = new_category
        else:
            category = Category.objects.get(id=cat_id)

        
        image = request.POST.get('image')
        owner = request.user


        # Attempt to create new product
        try:
            product = Product.objects.create(name=name, description=description, price=price, category=category, image=image, owner=owner)
        except KeyError:
            return render(request, "auctions/create.html", {
                "message": "Please fill out all fields"
            })


        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/create.html", {'categories': categories})


def showproduct(request, title):  
    product = get_object_or_404(Product, name=title)
    comments = product.comments_of_product.all()
    if not comments:
        comments = []
    else:
        comments = list(product.comments_of_product.all())[::-1]
    
    if request.user.is_authenticated: 
        
        user = request.user

        has_bids = Bid.objects.filter(product=product).exists()

        if has_bids:
            somebody_bid = True
        else:
            somebody_bid = False

        if product.watchlisted_by.filter(id=user.id).exists():
            added = True
        else:
            added = False

        if user.id == product.owner.id:
            owned_by_user = True
        else:
            owned_by_user = False

        if product.active == False:
            highest_bid = Bid.objects.filter(product=product).aggregate(max_bid=Max('bid'))
            winning_bid = Bid.objects.get(product=product, bid=highest_bid['max_bid'])
            return render(request, "auctions/product.html", {'title': title, 'product': product, 'winning_bid': winning_bid, 'owned_by_user': owned_by_user, 'added': added, 'somebody_bid': somebody_bid})
        
        return render(request, "auctions/product.html", {'title': title, 'product': product, 'owned_by_user': owned_by_user, 'added': added, 'somebody_bid': somebody_bid, 'comments': comments})

    else:
        
        return render(request, "auctions/product.html", {'title': title, 'product': product, 'comments': comments})

@login_required
def add_to_watchlist(request, title):
    product = get_object_or_404(Product, name=title)
    product.watchlisted_by.add(request.user)
    return redirect('showproduct', title=product.name)


@login_required
def remove_from_watchlist(request, title):
    product = get_object_or_404(Product, name=title)
    product.watchlisted_by.remove(request.user)
    return redirect('showproduct', title=product.name)


def watchlist(request):
    user = request.user
    watchlist_products = user.watchlist.all()
    watchlist_title = f"{user}'s Watchlist"

    return render(request, "auctions/index.html", {'products': watchlist_products, 'category': watchlist_title})



@login_required
def edit(request, title):

    product = get_object_or_404(Product, name=title)
    exlusion = product.category.category
    categories = Category.objects.exclude(category=exlusion)
    comments = product.comments_of_product.all()
    if not comments:
        comments = []
    else:
        comments = list(product.comments_of_product.all())[::-1]

    has_bids = Bid.objects.filter(product=product).exists()

    if has_bids:
        somebody_bid = True
    else:
        somebody_bid = False

    if request.method == "POST":
        name = request.POST["name"]
        description = request.POST["description"]
        
        cat_id = request.POST.get('category')
        category = Category.objects.get(id=cat_id)

        image = request.POST.get('image')
        owner = request.user

        # Update product fields
        product.name = name
        product.description = description
        
        product.category = category
        product.image = image
        product.owner = owner

        # Save the updated product
        product.save()
        owned_by_user = True



        return render(request, "auctions/product.html", {'title': product.name, 'product': product,'owned_by_user': owned_by_user, 'somebody_bid': somebody_bid, 'comments': comments})
    else:
        return render(request, "auctions/edit.html", {'title': title, 'product': product, 'categories': categories})
   
@login_required
def bid(request, title):
    bid = request.POST["bid"]
    bidder = request.user
    product = get_object_or_404(Product, name=title)
    

    comments = product.comments_of_product.all()
    if not comments:
        comments = []
    else:
        comments = list(product.comments_of_product.all())[::-1]

    if not bid:
        owned_by_user = False 
        message = 'Bid must be greater than or equal to current bid.'
        return render(request, "auctions/product.html", {'title': title, 'product': product, 'owned_by_user': owned_by_user, 'message':message, 'somebody_bid': somebody_bid, 'comments': comments})

    if float(bid) >= product.price:
        # Create new bid
        new_bid = Bid.objects.create(bid=bid,bidder=bidder,product=product)

        # Update current bid field
        product.price = bid
        product.save()

        owned_by_user = False 
        if product.watchlisted_by.filter(id=bidder.id).exists():
            added = True
        else:
            added = False

        return render(request, "auctions/product.html", {'title': title, 'product': product, 'owned_by_user': owned_by_user, "new_bid":new_bid, "added": added, 'somebody_bid': somebody_bid, 'comments': comments})
    else: 
        owned_by_user = False 
        message = 'Bid must be greater than or equal to current bid.'
        return render(request, "auctions/product.html", {'title': title, 'product': product, 'owned_by_user': owned_by_user, 'message':message, 'somebody_bid': somebody_bid, 'comments': comments})


@login_required
def close(request, title):
    product = get_object_or_404(Product, name=title)
    user = request.user
    
    comments = product.comments_of_product.all()
    if not comments:
        comments = []
    else:
        comments = list(product.comments_of_product.all())[::-1]


    if product.owner == user:
        product.active = False
        product.save()

    highest_bid = Bid.objects.filter(product=product).aggregate(max_bid=Max('bid'))
    winning_bid = Bid.objects.get(product=product, bid=highest_bid['max_bid'])

    return render(request, "auctions/product.html", {'title': title, 'product': product, 'winning_bid': winning_bid, 'somebody_bid': somebody_bid, 'comments': comments})


@login_required
def comment(request, title):
    product = get_object_or_404(Product, name=title)
    user = request.user

    comment = request.POST["comment"]

    new_comment = Comment.objects.create(author=user, comment=comment, product=product)

    comments = product.comments_of_product.all()
    comments = list(product.comments_of_product.all())[::-1]

    if user.id == product.owner.id:
        owned_by_user = True
    else:
        owned_by_user = False

    has_bids = Bid.objects.filter(product=product).exists()

    if has_bids:
        somebody_bid = True
    else:
        somebody_bid = False


    return render(request, "auctions/product.html", {'title': title, 'product': product, 'somebody_bid': somebody_bid, 'comments': comments, 'owned_by_user': owned_by_user})


def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {'categories': categories})

def show_ctg(request, category):
    # Get active listings whose category is 'category' and reverse them so that most recently added listing is shown on top
    category = Category.objects.get(category=category)
    products = Product.objects.filter(active=True, category=category)

    has_products = Product.objects.filter(active=True, category=category).exists()
    if not has_products:
        message = 'No such products listed at this time.'
    else:
        message = []

    reversed_products = sorted(products, key=lambda x: x.id, reverse=True)
    return render(request, "auctions/index.html", {'products': reversed_products, 'message': message, 'category': category.category})

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass


class Category(models.Model):
    category = models.CharField(max_length=255)

    def __str__(self):
        return f"Category {self.id}: {self.category}"

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="categories", default=1)
    image = models.CharField(max_length=200, null=True)
    watchlisted_by = models.ManyToManyField(User,default=1, related_name='watchlist')
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner", default=1)

    def __str__(self):
        return f"{self.id} {self.name} ({self.category.category}), fav'd by {self.watchlisted_by.all()}"


class Bid(models.Model):
    bid = models.DecimalField(max_digits=8, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="whatbid")
    won = models.BooleanField(default=False) 
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.bidder} bid ${self.bid} on '{self.product.name}'."


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    comment = models.TextField(max_length=1000)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="comments_of_product", default=1)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.author}: '{self.comment}'."

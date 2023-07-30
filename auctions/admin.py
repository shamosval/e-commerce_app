from django.contrib import admin
from .models import Product, Bid, Comment, Category

# Register your models here.
admin.site.register(Product)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Category)

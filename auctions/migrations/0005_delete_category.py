# Generated by Django 4.2.2 on 2023-06-28 20:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_remove_product_category'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Category',
        ),
    ]

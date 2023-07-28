import random
from django.conf import settings
from django.contrib import admin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
from uuid import uuid4

# Create your models here.


class Promotion(models.Model):
    code = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    discount = models.FloatField()


class Genre(models.Model):
    title = models.CharField(max_length=255)
   
    def __str__(self):
        return str(self.title)
    
    class Meta:
        ordering = ['title']


class Movie(models.Model):
    AGE_RATING_GENERAL = 'G'
    AGE_RATING_PG = 'PG'
    AGE_RATING_PG13 = 'PG13'
    AGE_RATING_R = 'R'
    AGE_RATING_CHOICES = [
        (AGE_RATING_GENERAL, 'General'),
        (AGE_RATING_PG, 'Parental Guidance'),
        (AGE_RATING_PG13, 'Parental Guidance 13'),
        (AGE_RATING_R, 'Adult rated'),
    ]

    id = models.CharField(max_length=5, primary_key=True)
    barcode = models.ImageField(upload_to='images/', blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    daily_rental_rate = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(1)])
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    last_updated = models.DateTimeField(auto_now=True)
    age_rating  = models.CharField(max_length=4, choices=AGE_RATING_CHOICES, default=AGE_RATING_GENERAL)
    genres = models.ManyToManyField(Genre, related_name='movie')
    
    
    
    def __str__(self):
        return str(self.title)
    
    class Meta:
        ordering = ['title']
    

    def save(self, *args, **kwargs):
        EAN = barcode.get_barcode_class('ean13')
        code = ''.join(random.choice('0123456789') for _ in range(10))
        total = [int(code[i]) * 3 if i % 2 == 0 else int(code[i]) for i in range(10)]
        unpacked_total = int(''.join(map(str, total)))
        ean = EAN(f'{unpacked_total}{self.id}', writer=ImageWriter())
        buffer = BytesIO()
        ean.write(buffer)
        self.barcode.save(f'{self.title}.png', File(buffer), save=False)
        return super().save(*args, **kwargs)



class Customer(models.Model):
    age = models.PositiveIntegerField(validators=[MinValueValidator(3), MaxValueValidator(100)], null=True, blank=True)
    phone = models.CharField(max_length=255)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name
    
    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']


class RentOrder(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]


    ORDER_STATUS_COLLECTED = 'C'
    ORDER_STATUS_LOST = 'L'
    ORDER_STATUS_RETURNED = 'R'
    ORDER_STATUS_CHOICES = [
        (ORDER_STATUS_COLLECTED, 'Collected'),
        (ORDER_STATUS_LOST, 'Lost'),
        (ORDER_STATUS_RETURNED, 'Returned')
    ]

    order_status = models.CharField(max_length=1, choices=ORDER_STATUS_CHOICES, default=ORDER_STATUS_COLLECTED)
    rent_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    payment_status = models.CharField(max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    class Meta:
        permissions = [
            ('cancel_order', 'Can cancel order')
        ]


class RentOrderItem(models.Model):
    rent_order = models.ForeignKey(RentOrder, on_delete=models.PROTECT)
    movie = models.ForeignKey(Movie, on_delete=models.PROTECT, related_name='rentorderitems')
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )
    
    class Meta:
        #Makes it possible for there not to be duplication. When trying to add or increase the number of
        #  a movie to a cart, instead of creating another cart, we would instead just increase only its quantity.
        unique_together = [['cart', 'movie']]

class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
from django.db import models
from django.conf import settings
from constants.payment import TRANSACTION_STATUS, PAYMENT_STATUS


class Plan(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"
    
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField()
    amount_due = models.IntegerField()
    amount_paid = models.IntegerField()
    attempts = models.IntegerField()
    currency = models.CharField(max_length=3, default='INR')
    gateway_order_id = models.CharField(max_length=100, unique=True)
    receipt = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    notes = models.JSONField(default=dict, blank=True)
    offer_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.gateway_order_id}"

class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    razorpay_order_id = models.CharField(max_length=100)
    signature = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=50)
    amount = models.IntegerField()
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction for Order {self.order.transaction_id}"



from rest_framework import serializers
from .models import Order, Transaction
from functions.send_email import send_payment_receipt


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"

    def save(self):
        transaction = super().save()
        self.send_payment_receipt_email()
        return transaction

    def send_payment_receipt_email(self):
        user = self.context["request"].user
        order_id = self.data.get("razorpay_order_id")
        transaction_id = self.data.get("razorpay_payment_id")
        name = user.get_full_name()
        email = user.email
        phone_number = getattr(user, "phone_number", None)
        order = Order.objects.filter(gateway_order_id=order_id).first()
        send_payment_receipt(order, name, phone_number, email, order_id, transaction_id)

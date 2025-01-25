from rest_framework import serializers
from .models import Order, Transaction
from functions.send_email import send_payment_receipt
from job_portal_django.settings import razorpay_client
from functions.common import (
    logger,
)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"

    def validate(self, data):
        request_data = self.context.get("request", {}).data
        required_fields = [
            "razorpay_order_id",
            "razorpay_payment_id",
            "razorpay_signature",
        ]

        for field in required_fields:
            if field not in request_data:
                raise serializers.ValidationError({field: f"{field} is required."})

        try:
            params = {
                "razorpay_order_id": request_data["razorpay_order_id"],
                "razorpay_payment_id": request_data["razorpay_payment_id"],
                "razorpay_signature": request_data["razorpay_signature"],
            }
            razorpay_client.utility.verify_payment_signature(params)
        except:
            raise serializers.ValidationError(
                {"signature": "Invalid Razorpay signature."}
            )

        return data

    def create(self, validated_data):
        transaction = super().create(validated_data)
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
        if not order:
            raise serializers.ValidationError(
                {"order": "Order not found for the given Razorpay order ID."}
            )
        send_payment_receipt(order, name, phone_number, email, order_id, transaction_id)

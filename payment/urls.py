from django.urls import path
from .views import *

urlpatterns = [
    path("create_order/", create_order, name="create_order"),
    path("capture_transaction/", capture_transaction, name="capture_transaction"),
    path("create_transaction/", create_transaction, name="create_transaction"),
    path("payment_details/", payment_details, name="payment_details"),

]

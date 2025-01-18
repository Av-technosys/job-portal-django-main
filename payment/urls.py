from django.urls import path
from .views import *

urlpatterns = [
    path("create_order/", create_order, name="create_order"),
    path("capture_transaction/", capture_transaction, name="capture_transaction"),
]

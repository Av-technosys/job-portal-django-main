from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import *
from handlers.common import *
from handlers.permissions import IsRecruiter, IsJobSeeker
from accounts.models import Subscription
from assessment.models import Attempt
from accounts.serializers import SubscriptionSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    return create_cart_order(Plan, Subscription, OrderSerializer, request)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def capture_transaction(request):
    return capture_transaction_data(
        TransactionSerializer, Attempt, SubscriptionSerializer, Plan,Order, request
    )

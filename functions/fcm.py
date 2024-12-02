from firebase_admin import messaging
from accounts.models import Notification, User
from functions.common import paginator, ResponseHandler, serializer_handle
from accounts.serializers import NotificationSerializer
from rest_framework import status
from types import SimpleNamespace
from constants.errors import RESPONSE_ERROR


def subscribe_to_topic(device_token, topic):
    response = messaging.subscribe_to_topic([device_token], topic)

    if response.success_count > 0:
        print(f"Successfully subscribed {device_token} to topic {topic}")
    else:
        print(f"Failed to subscribe {device_token} to topic {topic}")

    return response


def send_notification_to_topic(topic, title, body):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        topic=topic,
    )

    response = messaging.send(message)

    print(f"Notification sent to topic {topic}, response: {response}")


def unsubscribe_from_topic(device_token, topic):
    response = messaging.unsubscribe_from_topic([device_token], topic)

    if response.success_count > 0:
        print(f"Successfully unsubscribed {device_token} from topic {topic}")
    else:
        print(f"Failed to unsubscribe {device_token} from topic {topic}")

    return response


def list_notification(serializer, request):
    try:
        notification_instance = Notification.objects.filter(received_by=request.user.id)

        page_obj, count, total_pages = paginator(notification_instance, request)
        serializer = serializer(page_obj, many=True)
        response_data = {
            "total_count": count,
            "total_pages": total_pages,
            "current_page": page_obj.number,
            "data": serializer.data,
        }

        return ResponseHandler.success(response_data, status_code=status.HTTP_200_OK)

    except:
        return ResponseHandler.error(
            message=RESPONSE_ERROR, status_code=status.HTTP_400_BAD_REQUEST
        )


def save_notification(data, sent_from_id, received_by_id):
    try:
        user_details = User.objects.filter(id__in=[sent_from_id, received_by_id])
        mock_request = SimpleNamespace()
        mock_request.user = SimpleNamespace(id=user_details[0].id)
        mock_request.data = {
            **data,
            "sent_from": user_details[0].id,
            "received_by": user_details[1].id,
        }
        serializer_handle(NotificationSerializer, mock_request)

    except Exception as e:
        print(e, "error in saving notification")

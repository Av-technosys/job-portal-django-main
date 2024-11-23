from firebase_admin import messaging


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

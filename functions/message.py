from django.shortcuts import get_object_or_404
from functions.common import paginator, ResponseHandler, serializer_handle
from rest_framework import status
from constants.errors import RESPONSE_ERROR
from jobs.models import Communication, JobApply


def message_get_handle(serializer_class, request, application_id):
    try:
        message_instance = Communication.objects.filter(application=application_id)
        # Descending order of created date is the latest message
        message_instance = message_instance.order_by("created_date")

        page_obj, count, total_pages = paginator(message_instance, request)
        serializer = serializer_class(page_obj, many=True)
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


def message_post_handle(serializer_class, request, application_id):

    try:
        job_apply = get_object_or_404(JobApply, id=application_id)

        request.data["sent_from"] = request.user.id
        request.data["application"] = application_id

        if request.user.user_type == 1:
            request.data["received_by"] = job_apply.owner.id

        elif request.user.user_type == 2:
            request.data["received_by"] = job_apply.student.id

        return serializer_handle(serializer_class, request)

    except Exception as e:
        return ResponseHandler.error(
            message=RESPONSE_ERROR, status_code=status.HTTP_400_BAD_REQUEST
        )

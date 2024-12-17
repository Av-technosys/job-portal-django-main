from functions.common import *
from constants.errors import *
from functions.message import *


def request_handler(model, serializer, request):
    match request.method:
        case "GET":
            return get_handle(model, serializer, request)
        case "POST":
            return serializer_handle(serializer, request)
        case "PATCH":
            return update_handle(model, serializer, request)
        case "DELETE":
            return delete_handle(model, request)
        case _:
            return ResponseHandler.error(
                METHOD_ERROR, status_code=status.HTTP_405_METHOD_NOT_ALLOWED
            )


def message_handler(serializer_class, request, application_id):
    match request.method:
        case "GET":
            return message_get_handle(serializer_class, request, application_id)
        case "POST":
            return message_post_handle(serializer_class, request, application_id)
        case _:
            return ResponseHandler.error(
                METHOD_ERROR, status_code=status.HTTP_405_METHOD_NOT_ALLOWED
            )

def job_save_handler(serializer_class, JobSaved, request):
    try:
        user_id = request.user.id
        job_id = request.data.get("job")
        request.data["user"] = user_id

        if request.method == "GET":
            # Implementing filter_search_handler functionality
            q_filters, filter_kwargs = filters(request)

            owner_filters = {}
            if request.data.get("owner"):
                owner_filters["user_id__in"] = request.data.get("owner")

            # If job_ids is provided, filter the instances by job IDs
            if job_id:
                instances = JobSaved.objects.filter(id__in=[job_id])
            else:
                if not q_filters and not filter_kwargs and not owner_filters:
                    instances = JobSaved.objects.all()
                else:
                    instances = JobSaved.objects.filter(
                        q_filters, **filter_kwargs, **owner_filters
                    )

            if not instances.exists():
                return ResponseHandler.error(
                    message=ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
                )

            sort_fields = request.GET.getlist("sort[]", ["created_date"])
            instances = instances.order_by(*sort_fields)

            page_obj, count, total_pages = paginator(instances, request)
            serializer = serializer_class(page_obj, many=True, context={"request": request})
            response_data = {
                "total_count": count,
                "total_pages": total_pages,
                "current_page": page_obj.number,
                "data": serializer.data,
            }
            return ResponseHandler.success(response_data, status_code=status.HTTP_200_OK)

        elif request.method == "POST":
            return serializer_handle(serializer_class, request)

        elif request.method == "DELETE":
            instance = JobSaved.objects.get(job_id=job_id, user=request.user)
            if instance:
                instance.delete()
                return ResponseHandler.success(
                    {"message": REMOVE_SUCCESS}, status_code=status.HTTP_204_NO_CONTENT
                )
            return ResponseHandler.error(
                ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        logger.error(f"Error in job_save_handler: {e}")
        return ResponseHandler.error(
            RESPONSE_ERROR, status_code=status.HTTP_400_BAD_REQUEST
        )


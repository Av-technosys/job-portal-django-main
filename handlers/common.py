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


def job_save_handler(
    JobSaveSerializer, JobListSeekerViewSerializer, JobSaved, JobInfo, request
):
    try:
        user_id = request.user.id
        job_id = JobSaved.objects.filter(user=request.user).values_list(
            "job_id", flat=True
        )
        request.data["user"] = user_id

        if request.method == "GET":
            # Check if JobSaved table is empty
            if not JobSaved.objects.filter(user=request.user).exists():
                return ResponseHandler.error(
                    message=ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
                )
            # Implementing filter_search_handler functionality
            q_filters, filter_kwargs = filters(request)

            owner_filters = {}
            if request.data.get("owner"):
                owner_filters["user_id__in"] = request.data.get("owner")

            # If job_ids is provided, filter the instances by job IDs
            if job_id:
                instances = JobInfo.objects.filter(id__in=[job_id])
            else:
                instances = JobInfo.objects.filter(
                    q_filters, **filter_kwargs, **owner_filters
                )

            if not instances.exists():
                return ResponseHandler.error(
                    message=ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
                )

            sort_fields = request.GET.getlist("sort[]", ["created_date"])
            instances = instances.order_by(*sort_fields)

            page_obj, count, total_pages = paginator(instances, request)
            serializer = JobListSeekerViewSerializer(
                page_obj, many=True, context={"request": request}
            )
            response_data = {
                "total_count": count,
                "total_pages": total_pages,
                "current_page": page_obj.number,
                "data": serializer.data,
            }
            return ResponseHandler.success(
                response_data, status_code=status.HTTP_200_OK
            )

        elif request.method == "POST":
            return serializer_handle(JobSaveSerializer, request)

        elif request.method == "DELETE":
            if not job_id:
                return ResponseHandler.error(
                    message=ERROR_STUDENT_ID_REQUIRED,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Attempt to delete the CandidateSaved instances
            instances = JobSaved.objects.filter(job__in=job_id, user=user_id)
            deleted_count, _ = (
                instances.delete()
            )  # Delete and get the count of deleted instances

            if deleted_count > 0:
                return ResponseHandler.success(
                    {"message": {REMOVE_SUCCESS}},
                    status_code=status.HTTP_204_NO_CONTENT,
                )
            return ResponseHandler.error(
                message=ERROR_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
            )
    except Exception as e:
        logger.error(e)
        return ResponseHandler.error(
            RESPONSE_ERROR, status_code=status.HTTP_400_BAD_REQUEST
        )


def candidate_save_handler(
    CandidateSaveSerializer,
    ListCandidateSerializer,
    CandidateSaved,
    StudentProfile,
    request,
):
    try:
        user_id = request.user.id
        student_id = CandidateSaved.objects.filter(recruiter=user_id).values_list(
            "student_id", flat=True
        )
        request.data["recruiter"] = user_id  # Set the recruiter ID

        if request.method == "GET":  # Added GET method handling
            # Check if CandidateSaved table is empty
            if not CandidateSaved.objects.filter(recruiter=user_id).exists():
                return ResponseHandler.error(
                    message=ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
                )
            q_filters, filter_kwargs = filters(request)
            owner_filters = {}
            if request.data.get("owner"):
                owner_filters["user_id__in"] = request.data.get("owner")
            if student_id:
                instances = StudentProfile.objects.filter(user__in=student_id)
            else:
                instances = StudentProfile.objects.filter(
                    q_filters, **filter_kwargs, **owner_filters
                )

            if not instances.exists():
                return ResponseHandler.error(
                    message=ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
                )

            sort_fields = request.GET.getlist("sort[]", ["created_date"])
            instances = instances.order_by(*sort_fields)

            page_obj, count, total_pages = paginator(instances, request)
            serializer = ListCandidateSerializer(
                page_obj, many=True, context={"request": request}
            )
            response_data = {
                "total_count": count,
                "total_pages": total_pages,
                "current_page": page_obj.number,
                "data": serializer.data,
            }
            return ResponseHandler.success(
                response_data, status_code=status.HTTP_200_OK
            )

        if request.method == "POST":
            return serializer_handle(CandidateSaveSerializer, request)

        elif request.method == "DELETE":
            # Attempt to delete the CandidateSaved instances
            instances = CandidateSaved.objects.filter(
                student__in=student_id, recruiter=user_id
            )
            deleted_count, _ = (
                instances.delete()
            )  # Delete and get the count of deleted instances

            if deleted_count > 0:
                return ResponseHandler.success(
                    {"message": {REMOVE_SUCCESS}},
                    status_code=status.HTTP_204_NO_CONTENT,
                )
            return ResponseHandler.error(
                message=ERROR_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
            )
    except Exception as e:
        logger.error(e)
        return ResponseHandler.error(
            RESPONSE_ERROR, status_code=status.HTTP_400_BAD_REQUEST
        )


def job_details_by_job_id(model, job_id, serializer_class, request):
    try:
        instances = model.objects.get(pk=job_id)
        serializer = serializer_class(instances)
        return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(e)
        return ResponseHandler.error(
            RESPONSE_ERROR, status_code=status.HTTP_400_BAD_REQUEST
        )

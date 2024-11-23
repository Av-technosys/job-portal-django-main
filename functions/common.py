from rest_framework.request import Request
import random
from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils import timezone
import os
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404


def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))


from constants.errors import *
from rest_framework.response import Response


def get_flattened_error_message(message):
    if isinstance(message, list):
        return next(iter(message.values()))[0]
    else:
        return message


class ResponseHandler:

    @staticmethod
    def success(data=None, status_code=200):
        response_data = {
            "success": True,
            "data": remove_unwanted_id_from_response(data),
        }
        return Response(response_data, status=status_code)

    @staticmethod
    def error(message=RESPONSE_ERROR, status_code=400):
        response_data = {
            "success": False,
            "message": get_flattened_error_message(message),
        }
        return Response(response_data, status=status_code)

    @staticmethod
    def api_exception_error(message=RESPONSE_ERROR):
        return APIException({"message": message, "success": False})


def get_login_request_payload(request: Request, key: str, default=None):
    return request.data.get(key, default)


def remove_unwanted_id_from_response(data):
    if isinstance(data, list) and len(data) == 0:
        pass
    elif isinstance(data, list) and len(data) > 0:
        for d in data:
            if isinstance(d, object):
                d.pop("user", "")
    elif isinstance(data, object):
        # Removes user as a foreign key from the response
        data.pop("user", "")
    return data


def serializer_handle(Serializers, request):
    try:
        if request.user.id:
            request.data["user"] = request.user.id
        serializer = Serializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseHandler.success(
                serializer.data, status_code=status.HTTP_201_CREATED
            )
        return ResponseHandler.error(
            serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception:
        return ResponseHandler.error(
            RESPONSE_ERROR, status_code=status.HTTP_400_BAD_REQUEST
        )


def serializer_handle_customize_response_only_validate(Serializers, request):
    if request.user.id:
        request.data["user"] = request.user.id
    serializer = Serializers(data=request.data)
    if serializer.is_valid():
        responseData = serializer.return_response(serializer.data)
        return ResponseHandler.success(
            responseData, status_code=status.HTTP_201_CREATED
        )
    return ResponseHandler.error(
        serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
    )


def serializer_handle_customize_response(Serializers, request):
    serializer = Serializers(data=request.data)
    if serializer.is_valid():
        responseData = serializer.save()
        return ResponseHandler.success(
            responseData, status_code=status.HTTP_201_CREATED
        )
    return ResponseHandler.error(
        serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
    )


def update_handle(model_class, serializer_class, request):
    try:
        id = request.data.get("id")
        instance = model_class.objects.get(id=id, user=request.user)
    except model_class.DoesNotExist:
        return ResponseHandler.error(
            f"{model_class.__name__} {ERROR_NOT_FOUND}",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    serializer = serializer_class(instance, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)
    return ResponseHandler.error(
        serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
    )


def get_customize_handler(model, serializer_class, pk):
    instances = model.objects.filter(**pk)
    serializer = serializer_class(instances, many=True)
    return ResponseHandler.success(serializer.data[0], status_code=status.HTTP_200_OK)


def get_handle_profile(model, serializer_class, request):
    try:
        instance = model.objects.get(user=request.user.id)
        serializer = serializer_class(instance)
        return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)
    except model.DoesNotExist:
        return ResponseHandler.error(
            ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )


def get_handle(model, serializer_class, request):
    instances = model.objects.filter(user=request.user)
    serializer = serializer_class(instances, many=True)
    return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)


def delete_handle(model, request):
    instance_id = request.data.get("id")
    instances = model.objects.filter(id=instance_id, user=request.user)
    if instances.exists():
        instances.delete()
        return ResponseHandler.success(
            {"message": REMOVE_SUCCESS}, status_code=status.HTTP_204_NO_CONTENT
        )
    return ResponseHandler.error(ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND)


def upload_handler(model, serializer_class, request):
    if request.method == "GET":
        return get_handle(model, serializer_class, request)

    elif request.method == "POST":
        if request.user.id:
            request.data["user"] = request.user.id
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "PATCH":
        try:
            document_id = request.data.get("id")
            document = model.objects.get(id=document_id, user=request.user)
        except model.DoesNotExist:
            return ResponseHandler.error(
                ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
            )

        if "file" in request.FILES:
            old_file = document.file
            new_file = request.FILES["file"]

            if old_file:
                old_file.delete(save=False)
            document.file = new_file
        if request.user.id:
            request.data["user"] = request.user.id

        serializer = serializer_class(document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        instance_id = request.data.get("id")
        instance = model.objects.get(id=instance_id, user=request.user)
        if instance.file:
            instance.file.delete(save=False)
            instance.delete()
            return ResponseHandler.success(
                data={"message": REMOVE_SUCCESS}, status_code=status.HTTP_204_NO_CONTENT
            )
        return ResponseHandler.error(
            ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )


def file_rename(instance, filename):
    ext = filename.split(".")[-1]
    timestamp = timezone.now().timestamp()
    new_filename = f"{timestamp}.{ext}"
    return os.path.join(f"documents/{instance.file_type}/", new_filename)


def get_data_from_id_and_serialize(model, serializer_class, obj_id):
    try:
        obj = model.objects.get(id=obj_id)
        serializer = serializer_class(obj)
        return ResponseHandler.success(serializer.data)
    except model.DoesNotExist:
        return ResponseHandler.error(
            {"error": f"{model.__name__} not found"}, status=status.HTTP_404_NOT_FOUND
        )


def filters(request):
    q_filters = Q()
    filter_kwargs = {}

    if filter_result := request.data.get("search"):
        if "filter_job_seeker" in request.path:
            q_filters = (
                Q(user__academicqualification__specialization__icontains=filter_result)
                | Q(short_bio__icontains=filter_result)
                | Q(user__skillset__skill_name__icontains=filter_result)
                | Q(designation__icontains=filter_result)
            )
        elif "list_jobs" in request.path:
            q_filters = (
                Q(designation__icontains=filter_result)
                | Q(contact_and_skills__skills_required__icontains=filter_result)
                | Q(job_description__job_title__icontains=filter_result)
            )

    filter_mappings = {
        "education": "user__academicqualification__specialization__in",
        "location": "city__in",
        "experience": "experience__in",
        "skills": "user__skillset__skill_name__in",
        "salary_expectations": "expecting_salary__in",
        "job_location": "location__in",
        "job_type": "job_type__in",
        "skills": "contact_info__skills_required__in",
    }

    for key, filter_key in filter_mappings.items():
        if terms := request.data.get(key):
            if isinstance(terms, list):
                filter_kwargs[filter_key] = terms

    return q_filters, filter_kwargs


def filter_search_handler(model_class, serializer_class, request):
    q_filters, filter_kwargs = filters(request)

    try:
        if not q_filters and not filter_kwargs:
            instances = model_class.objects.all()

        else:
            instances = model_class.objects.filter(q_filters, **filter_kwargs)

        if not instances.exists():
            ResponseHandler.error(
                message=ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
            )

        sort_fields = request.data.get("sort", ["created_date"])
        instances = instances.order_by(*sort_fields)

        page_obj, count, total_pages = paginator(instances, request)
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
            RESPONSE_ERROR, status_code=status.HTTP_400_BAD_REQUEST
        )


def paginator(queryset, request):
    if not queryset.ordered:
        queryset = queryset.order_by("created_date")
    page_size = int(request.GET.get("page_size", 10))
    paginator = Paginator(queryset, page_size)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    return page_obj, paginator.count, paginator.num_pages


def job_apply_handler(serializer_class, StudentProfile, request):
    try:
        if request.user.user_type == 2:
            return ResponseHandler.error(
                message=ERROR_INVALID_CREDENTIALS,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        student_id = get_object_or_404(StudentProfile, user=request.user).id
        request.data["student"] = student_id
        return serializer_handle(serializer_class, request)
    except:
        return ResponseHandler.error(
            RESPONSE_ERROR, status_code=status.HTTP_400_BAD_REQUEST
        )


def application_handler(
    modal_class, serializer_class, profile, profile_serializer, student_profile, request
):
    user_type = request.user.user_type
    try:
        if user_type == 1:
            student_id = get_object_or_404(student_profile, user=request.user).id
            _id = list(
                modal_class.objects.filter(student_id=student_id).values_list(
                    "job_id", flat=True
                )
            )
            return get_application_data(
                _id,
                modal_class,
                serializer_class,
                profile,
                profile_serializer,
                request,
                "job",
            )

        elif user_type == 2:
            id = request.data.get("id")
            if not id:
                return ResponseHandler.error(
                    message=ERROR_JOB_ID_REQUIRED,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            _id = list(
                modal_class.objects.filter(job_id=id).values_list(
                    "student_id", flat=True
                )
            )
            return get_application_data(
                _id,
                modal_class,
                serializer_class,
                profile,
                profile_serializer,
                request,
                "student",
            )

    except:
        return ResponseHandler.error(
            message=RESPONSE_ERROR, status_code=status.HTTP_400_BAD_REQUEST
        )


def get_application_data(
    _id, modal_class, serializer_class, profile, profile_serializer, request, lookup
):
    try:
        if lookup == "student":
            instances = modal_class.objects.filter(student_id__in=_id).select_related(
                lookup
            )
        elif lookup == "job":
            instances = modal_class.objects.filter(job_id__in=_id).select_related(
                lookup
            )

        if not instances.exists():
            return ResponseHandler.error(
                message=ERROR_NO_APPLICATIONS_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        applications = serializer_class(instances, many=True)
        related_ids = [application.get(lookup) for application in applications.data]
        related_profiles = profile.objects.filter(id__in=related_ids)

        page_obj, count, total_pages = paginator(related_profiles, request)
        serializer = profile_serializer(page_obj, many=True)
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


def handle_application_status(model, serializer_class, request):
    if request.method == "GET":
        _id = request.data.get("id")

        if not _id:
            return ResponseHandler.error(status_code=status.HTTP_400_BAD_REQUEST)

        try:
            instance = model.objects.filter(job_id=_id)
            if not instance.exists():
                return ResponseHandler.error(
                    ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
                )

            serializer = serializer_class(instance, many=True)
            return ResponseHandler.success(
                serializer.data, status_code=status.HTTP_200_OK
            )

        except:
            return ResponseHandler.error(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    elif request.method in ["PATCH"]:
        try:
            job_id = request.data.get("job_id")
            student_id = request.data.get("student_id")

            if not job_id or not student_id:
                return ResponseHandler.error(
                    RESPONSE_ERROR, status_code=status.HTTP_400_BAD_REQUEST
                )
            instance = model.objects.filter(
                student_id=student_id, job_id=job_id
            ).first()
            if not instance:
                return ResponseHandler.error(
                    ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
                )
            serializer = serializer_class(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return ResponseHandler.success([], status_code=status.HTTP_200_OK)

            return ResponseHandler.error(
                serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
            )

        except:
            return ResponseHandler.error(
                RESPONSE_ERROR, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

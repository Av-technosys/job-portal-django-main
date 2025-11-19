from rest_framework.request import Request
import random
import string
from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils import timezone
import os
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
import logging
from datetime import datetime
from datetime import timedelta
import time
from job_portal_django.settings import razorpay_client
from django.db.models import F
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse

# from weasyprint import HTML
from io import BytesIO
from django.template.loader import render_to_string
from constants.payment import *


def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))


from constants.errors import *
from rest_framework.response import Response
from constants.common import USER_TYPE
from constants.user_profiles import JOB_SEEKER_DOCUMENT_TYPES, RECRUITER_DOCUMENT_TYPES
from constants.jobs import JOB_POST_STATUS_FEILDS, JOB_STATUS_UPDATED

logger = logging.getLogger("django")


def get_flattened_error_message(message):
    if isinstance(message, list) and "values" in message:
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
        if "message" in message and isinstance(message["message"], list):
            message = message["message"][0]
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
        serializer = Serializers(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return ResponseHandler.success(
                serializer.data, status_code=status.HTTP_201_CREATED
            )
        return ResponseHandler.error(
            serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
        )
    
    except APIException as api_error:
        # Handle serializer or custom API exceptions cleanly
        logger.warning(f"APIException in serializer_handle: {api_error.detail}")
        print("APIException in serializer_handle: ", api_error.detail)
        return ResponseHandler.error(
            api_error.detail, status_code=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        print("error in serializer_handle: ", e)
        logger.error(f"Error in serializer_handle: {e}", exc_info=True)
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

def job_seeker_details_handler(user_model,   serializer_class, request, job_seeker_id):
    try:
        user_instance = user_model.objects.get(id=job_seeker_id)
    except user_model.DoesNotExist:
        return ResponseHandler.error(
            "User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    print("user_instance", user_instance)
    serializer = serializer_class(user_instance) 
    return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)



def get_customize_handler(model, serializer_class, pk, request):
    try:
        instances = model.objects.filter(**pk)
        # print("instances: ", instances)
        serializer = serializer_class(
            instances, many=True, context={"request": request}
        )
        return ResponseHandler.success(
            serializer.data[0], status_code=status.HTTP_200_OK
        )
    except model.DoesNotExist:
        return ResponseHandler.error(
            ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )


def get_customize_handlerAdmin(model, serializer_class,job_seeker_id):
    try:
        instances = model.objects.filter(id= job_seeker_id)
        # print("instances: ", instances)
        serializer = serializer_class(
            instances, many=True
        )
        return ResponseHandler.success(
            serializer.data[0], status_code=status.HTTP_200_OK
        )
    except model.DoesNotExist:
        return ResponseHandler.error(
            ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )

def get_admin_meta_details_handler(organizationInfoModel, studentProfileModle, assessmentModel, request):
    data = {
        "recruiter_count": organizationInfoModel.objects.count(),
        "job_seeker_count": studentProfileModle.objects.count(),
        "assessment_count": assessmentModel.objects.count(),
    }
    return ResponseHandler.success(data, status_code=status.HTTP_200_OK)

def get_handle_profile(model, serializer_class, request):
    try:
        instance = model.objects.get(user=request.user.id)
        serializer = serializer_class(instance)
        return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)
    except model.DoesNotExist:
        return ResponseHandler.error(
            ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )
    

def get_handle_profile_admin(model, serializer_class, request, job_seeker_id):
    print("job_seeker_id: ", job_seeker_id)
    try:
        instance = model.objects.get(user=job_seeker_id)
        print("instance: ", instance)
        serializer = serializer_class(instance)
        print("serializer: ", serializer)
        return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)
    except model.DoesNotExist:
        return ResponseHandler.error(
            ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )


def get_handle(model, serializer_class, request):
    instances = model.objects.filter(user=request.user)
    serializer = serializer_class(instances, many=True)
    return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)



def get_handle_by_userid(model, serializer_class, userid):
    instances = model.objects.filter(user=userid)
    serializer = serializer_class(instances, many=True)
    return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)


def delete_handle(model, request):
    instance_id = request.data.get("id")
    instances = model.objects.filter(id=instance_id)
    if instances.exists():
        instances.delete()
        return ResponseHandler.success(
            {"message": REMOVE_SUCCESS}, status_code=status.HTTP_204_NO_CONTENT
        )
    return ResponseHandler.error(ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND)

def user_status_handle(model, request, active_status):
    user_id = request.data.get("id") 
    instances = model.objects.filter(id=user_id)
    if instances.exists():
        instances.update(is_active=active_status)
        return ResponseHandler.success(
            {"message": "Status updated to " + ("active" if active_status else "inactive")}, status_code=status.HTTP_204_NO_CONTENT
        )
    return ResponseHandler.error(ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND)


def upload_profile_image_handler(model, serializer_class, request):
    # Not added profile_image as a constant since this is common for job seeker / recruiter
    if request.method == "POST":
        if request.user.id:
            request.data["user"] = request.user.id
            request.data["file_type"] = "profile_image"

        try:
            document = model.objects.get(user=request.user, file_type="profile_image")

            if "file" in request.FILES:
                old_file = document.file
                new_file = request.FILES["file"]

                if old_file:
                    old_file.delete(save=False)
                document.file = new_file

            serializer = serializer_class(document, data=request.data, partial=True)

        except model.DoesNotExist:
            serializer = serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        # This will always return one element, since we are restricting creation by 1
        instance = model.objects.get(user=request.user, file_type="profile_image")
        if instance.file:
            instance.file.delete(save=False)
            instance.delete()
            return ResponseHandler.success(
                data={"message": REMOVE_SUCCESS}, status_code=status.HTTP_204_NO_CONTENT
            )
        return ResponseHandler.error(
            ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )


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


def upload_document_handler(model, serializer_class, request):
    if request.method == "GET":
        instances = model.objects.filter(user=request.user).exclude(
            file_type=JOB_SEEKER_DOCUMENT_TYPES[2][0]
        )
        serializer = serializer_class(instances, many=True)
        return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)

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


def question_file_rename(instance, filename):
    """
    Rename uploaded question image file uniquely for each question.
    Path: documents/assessment/<subject_id>/<timestamp>.<ext>
    """
    ext = filename.split(".")[-1]
    timestamp = int(timezone.now().timestamp())
    new_filename = f"{timestamp}.{ext}"

    # Use subject ID if available, otherwise fallback to 'general'
    subject_part = f"subject_{instance.subject.id}" if instance.subject_id else "general"

    return os.path.join(f"documents/assessment/{subject_part}/", new_filename)

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
            {"error": f"{model.__name__} not found"}
        )

def get_data_from_user_id_and_serialize(model, serializer_class, obj_id):
    try:
        obj = model.objects.get(user_id=obj_id)
        serializer = serializer_class(obj)
        return ResponseHandler.success(serializer.data)
    except model.DoesNotExist:
        return ResponseHandler.error(
            {"error": f"{model.__name__} not found"}
        )

def filters(request):
    q_filters = Q()
    filter_kwargs = {}

    if filter_result := request.GET.get("search"):
        if "filter_job_seeker" in request.path:
            q_filters = (
                Q(user__academicqualification__specialization__icontains=filter_result)
                | Q(short_bio__icontains=filter_result)
                | Q(user__skillset__skill_name__icontains=filter_result)
                | Q(designation__icontains=filter_result)
            )
        elif "list_jobs" in request.path:
            q_filters = Q(title__icontains=filter_result)
        elif "list_recruiters" in request.path:
            q_filters = Q(first_name=filter_result) | Q(
                company_description__icontains=filter_result
            )
        elif "list_all_recruiter" in request.path:
            q_filters = Q(user__first_name__icontains=filter_result)
        elif "list_all_job_seeker" in request.path:
            q_filters = Q(user__first_name__icontains=filter_result)

    filter_mappings = {
        "education": "user__academicqualification__specialization__in",
        "location": "city__in",
        "experience": "experience__in",
        "skills": "user__skillset__skill_name__in",
        "salary_expectations": "expecting_salary__in",
        "job_location": "location__in",
        "job_type": "job_type__in",
        "skills": "contact_info__skills_required__in",
        "company_location": "city__in",
        "company_state": "state__in",
        "company_country": "country__in",
    }

    for key, filter_key in filter_mappings.items():
        if terms := request.GET.getlist(f"{key}[]"):
            if isinstance(terms, list):
                filter_kwargs[filter_key] = terms

    return q_filters, filter_kwargs


def exlcude(request, instances):
    if "list_jobs" in request.path:
        if is_job_seeker(request=request):
            # Exludes jobs which are already applied by the logged in user
            return instances.exclude(job_id_applied__student=request.user.id)
    return instances


def filter_search_handler(model_class, serializer_class, request):
    q_filters, filter_kwargs = filters(request)
    # print(q_filters, filter_kwargs)
    owner_filters = {}
    if request.data.get("owner"):
        owner_filters["user_id__in"] = request.data.get("owner")

    try:
        if not q_filters and not filter_kwargs and not owner_filters:
            instances = model_class.objects.all()

        else:
            print( "print details: " , q_filters, filter_kwargs, owner_filters)
            instances = model_class.objects.filter(
                q_filters, **filter_kwargs, **owner_filters
            )

        if not instances.exists():
            ResponseHandler.error(
                message=ERROR_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
            )

        sort_fields = request.GET.getlist("sort[]", ["created_date"])
        instances = instances.order_by(*sort_fields)

        instances = exlcude(request=request, instances=instances)
        page_obj, count, total_pages = paginator(instances, request)
        serializer = serializer_class(page_obj, many=True, context={"request": request})
        response_data = {
            "total_count": count,
            "total_pages": total_pages,
            "current_page": page_obj.number,
            "data": serializer.data,
        }
        return ResponseHandler.success(response_data, status_code=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in filter_search_handler: {e}")
        return ResponseHandler.error(
            RESPONSE_ERROR, status_code=status.HTTP_400_BAD_REQUEST
        )
    

def get_job_listing(model_class, serializer_class, request):
    try:
        q_filters = Q()

        categories = request.GET.getlist("category")
        job_types = request.GET.getlist("jobType")
        experience_levels = request.GET.getlist("experience")
        date_posted_filters = request.GET.getlist("datePosted")
        search_filters = request.GET.getlist("search")

        if categories:
            q_filters &= Q(role__in=categories)

        if job_types:
            q_filters &= Q(job_type__in=job_types)

        if search_filters: 
            q_filters &= Q(title__icontains=search_filters[0])

        if experience_levels:
            q_filters &= Q(jd_fk_ji__experience__in=experience_levels)

        if date_posted_filters:
            now = timezone.now()
            if "Last_Hour" in date_posted_filters:
                q_filters &= Q(created_date__gte=now - timedelta(hours=1))
            elif "Last_24_Hours" in date_posted_filters:
                q_filters &= Q(created_date__gte=now - timedelta(days=1))
            elif "Last_7_Days" in date_posted_filters:
                q_filters &= Q(created_date__gte=now - timedelta(days=7))
            elif "Last_30_Days" in date_posted_filters:
                q_filters &= Q(created_date__gte=now - timedelta(days=30))
            elif "All" in date_posted_filters:
                pass

        instances = model_class.objects.filter(q_filters).distinct()

        if not instances.exists():
            return ResponseHandler.success(
                [], status_code=status.HTTP_200_OK
            )

        sort_fields = [field for field in request.GET.getlist("sort") if field.strip()] or ["-created_date"]
        instances = instances.order_by(*sort_fields)

        instances = exlcude(request=request, instances=instances)
        page_obj, count, total_pages = paginator(instances, request)

        serializer = serializer_class(page_obj, many=True, context={"request": request})

        response_data = {
            "total_count": count,
            "total_pages": total_pages,
            "current_page": page_obj.number,
            "data": serializer.data,
        }

        return ResponseHandler.success(response_data, status_code=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in get_job_listing: {e}")
        print(e)
        return ResponseHandler.error(
            "Something went wrong", status_code=status.HTTP_400_BAD_REQUEST
        )



def paginator(queryset, request):
    if not queryset.ordered:
        queryset = queryset.order_by("created_date")
    page_size = int(request.GET.get("page_size", 10))
    paginator = Paginator(queryset, page_size)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    return page_obj, paginator.count, paginator.num_pages


def job_apply_handler(serializer_class, JobInfo, request):
    try:
        # Student Id is used by logged in student user
        student_id = request.user.id
        job_id = request.data.get("job")
        job_owner_id = get_object_or_404(JobInfo, id=job_id).user_id
        request.data["student"] = student_id
        request.data["owner"] = job_owner_id
        request.data["job"] = job_id
        return serializer_handle(serializer_class, request)
    except Exception as e:
        logger.error(f"Error in job_apply_handler: {e}")
        return ResponseHandler.error(
            RESPONSE_ERROR, status_code=status.HTTP_400_BAD_REQUEST
        )


def application_handler(
    modal_class, serializer_class, profile, profile_serializer, request
):
    user_type = request.user.user_type
    try:
        if user_type == 1:
            related_profiles = modal_class.objects.filter(student_id=request.user.id)

        if user_type == 2:
            id = request.GET.get("id")
            if not id:
                _id = list(
                    modal_class.objects.filter(owner_id=request.user.id).values_list(
                        "student_id", flat=True
                    )
                )
            else:
                _id = list(
                    modal_class.objects.filter(job_id=id).values_list(
                        "student_id", flat=True
                    )
                )

            related_profiles = get_application_data(
                _id,
                modal_class,
                serializer_class,
                profile,
                "student",
            )

        if not related_profiles.exists():
            return ResponseHandler.error(
                message=ERROR_NO_APPLICATIONS_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        page_obj, count, total_pages = paginator(related_profiles, request)
        serializer = profile_serializer(page_obj, many=True)
        response_data = {
            "total_count": count,
            "total_pages": total_pages,
            "current_page": page_obj.number,
            "data": serializer.data,
        }
        return ResponseHandler.success(response_data, status_code=status.HTTP_200_OK)

    except Exception as err:
        logger.error(f"Error in application_handler: {err}")
        print(err)
        return ResponseHandler.error(
            message=RESPONSE_ERROR, status_code=status.HTTP_400_BAD_REQUEST
        )


def get_application_data(_id, modal_class, serializer_class, profile, lookup):
    try:
        if lookup == "student":
            instances = modal_class.objects.filter(student_id__in=_id).select_related(
                lookup
            )

        if not instances.exists():
            return instances

        applications = serializer_class(instances, many=True)
        related_ids = [application.get(lookup) for application in applications.data]

        if lookup == "student":
            related_profiles = profile.objects.filter(user_id__in=related_ids)

        return related_profiles
    except Exception as err:
        logger.error(f"Error in get_application_data: {err}")
        return ResponseHandler.error(
            message=RESPONSE_ERROR, status_code=status.HTTP_400_BAD_REQUEST
        )


def handle_application_status(model, serializer_class, request):
    if request.method in ["PATCH"]:
        try:
            job_id = request.data.get("job_id")
            student_id = request.data.get("student_id")
            print(job_id, student_id)
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


def get_todays_date():
    # Get today's date and format it
    today_date = datetime.today().strftime("%B %d, %Y")

    return today_date


def get_salary_formatted(JobInfo):
    # Assuming salary comes from `max_salary` and `min_salary` fields
    return f"{JobInfo.min_salary} - {JobInfo.max_salary}"


def get_location_formatted(JobInfo):
    try:
        description = JobInfo.jd_fk_ji
        if description:
            return f"{description.city}, {description.state}, {description.country}"
        return None
    except Exception:
        return None


def get_user_photo(user, Model):
    photo = Model.objects.filter(user=user, file_type="profile_image").first()
    return photo.file.url if photo and photo.file else None


def is_job_seeker(request):
    if (
        request
        and hasattr(request, "user")
        and request.user.is_authenticated
        and request.user.user_type == USER_TYPE[0][0]
    ):
        return True
    return False


def get_recruiter_profile_image(user):
    # Fetching with the foreign key related name
    photo = user.recruiter_upload_user_id.filter(
        file_type=RECRUITER_DOCUMENT_TYPES[2][0]
    ).first()
    return photo.file.url if photo and photo.file else None


def get_job_seeker_profile_image(user):
    # Fetching with the foreign key related name
    photo = user.job_seeker_upload_user_id.filter(
        file_type=JOB_SEEKER_DOCUMENT_TYPES[2][0]
    ).first()
    return photo.file.url if photo and photo.file else None


def get_job_seeker_documents(user, response_key_list):
    if user is not None:
        if hasattr(user, "job_seeker_upload_user_id"):
            # Exclude profile image
            return user.job_seeker_upload_user_id.exclude(
                file_type=JOB_SEEKER_DOCUMENT_TYPES[2][0]
            ).values(*response_key_list)
        else:
            return []
    else:
        return []


def get_recruiter_documents(user, response_key_list):
    if user is not None:
        if hasattr(user, "recruiter_upload_user_id"):
            # Exclude profile image
            return user.recruiter_upload_user_id.exclude(
                file_type=RECRUITER_DOCUMENT_TYPES[2][0]
            ).values(*response_key_list)
        else:
            return []
    else:
        return []


def get_days_remaining_for_job(jobInfo):
    if jobInfo.status == JOB_POST_STATUS_FEILDS[0][0]:
        now = timezone.now()
        time_difference = now - jobInfo.created_date

        # TBD Chore: Change 90 to whatever user has selected while creating job
        remaining_time = timedelta(days=90) - time_difference

        if remaining_time > timedelta(days=0):
            return remaining_time.days
        else:
            return None
    return None


def get_job_post_status(jobInfo):
    remaining_days = get_days_remaining_for_job(jobInfo=jobInfo)
    if remaining_days is None:
        # Expired
        return JOB_POST_STATUS_FEILDS[1][0]
    # Active
    return JOB_POST_STATUS_FEILDS[0][0]


def get_organization_type_from_models(obj):
    try:
        if hasattr(obj, "jd_fk_ji") and obj.jd_fk_ji:
            return obj.jd_fk_ji.organization_type or False
        return False
    except Exception as e:
        logger.error(f"Error getting organization type: {str(e)}")
        return False


def summary_counter_handler(
    job_applied_model, job_saved_model, profiles_saved_modal, job_posted_modal, request
):
    try:
        user_id = request.user.id
        user_type = request.user.user_type

        # Job Seeker
        if user_type == 1:
            applied_jobs_count = job_applied_model.objects.filter(
                student_id=user_id
            ).count()
            saved_jobs_count = job_saved_model.objects.filter(user_id=user_id).count()
            return ResponseHandler.success(
                data={"job_applied": applied_jobs_count, "saved_job": saved_jobs_count},
                status_code=status.HTTP_200_OK,
            )

        # Recruiter
        elif user_type == 2:
            saved_profiles_count = profiles_saved_modal.objects.filter(
                recruiter_id=user_id
            ).count()
            posted_jobs_count = job_posted_modal.objects.filter(user_id=user_id).count()
            return ResponseHandler.success(
                data={
                    "posted_jobs": posted_jobs_count,
                    "saved_profiles": saved_profiles_count,
                },
                status_code=status.HTTP_200_OK,
            )

    except:
        return ResponseHandler.error(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def generate_password_string(length=8):
    # Define the possible characters: lowercase, uppercase, and digits
    characters = string.ascii_letters + string.digits
    # Randomly choose characters from the pool to create the string
    random_string = "".join(random.choices(characters, k=length))
    return random_string


def get_expired_date(expiration_days):
    return timezone.now() + timedelta(days=expiration_days)

def get_razorpay_order(options):
    try:
        order = razorpay_client.order.create(data=options)
        return order
    except Exception as e:
        logger.error(f"Razorpay order creation failed: {str(e)}")
        return ResponseHandler.error(
            {"message": "Failed to create Razorpay order"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def create_cart_order(model_class, subscription_model, serializer_class, request):
           
            try:
                logger.info("create_cart_order() TRIGGERED")

                user_id = getattr(request.user, "id", None)
                planId = request.data.get("planId")
                logger.info("create_cart_order called", extra={"user_id": user_id, "planId": planId, "path": getattr(request, "path", None)})

                # Fetch plan price
                plan = model_class.objects.get(name=planId)
                amount = plan.price
                logger.debug("Fetched plan and price", extra={"planId": planId, "amount": amount})
                
                # Create Razorpay Order
                razorpay_order = get_razorpay_order(
                    {
                        "amount": amount * 100,
                        "currency": "INR",
                        "receipt": f"order_{user_id}_{int(time.time())}",
                    }
                )
                logger.debug("Razorpay order creation response", extra={"razorpay_order": razorpay_order})

                # If order creation failed
                if not isinstance(razorpay_order, dict) or "id" not in razorpay_order:
                    logger.error("Razorpay order creation failed or returned invalid response", extra={"user_id": user_id, "response": razorpay_order})
                    return ResponseHandler.error(
                        {"message": "Razorpay order creation failed"},
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                # Add extra fields before saving in DB
                razorpay_order["gateway_order_id"] = razorpay_order["id"]
                razorpay_order["user"] = user_id
                razorpay_order["plan_type"] = planId

               # Convert paise → rupees
                razorpay_order["amount"] = razorpay_order["amount"] // 100
                razorpay_order["amount_due"] = razorpay_order["amount_due"] // 100
                razorpay_order["amount_paid"] = razorpay_order["amount_paid"] // 100

                serializer = serializer_class(data=razorpay_order)
                if serializer.is_valid():
                    serializer.save()
                    logger.info("Saved razorpay order to DB", extra={"gateway_order_id": razorpay_order["gateway_order_id"], "user_id": user_id})
                    return ResponseHandler.success(
                        {
                            "gateway_order_id": razorpay_order["gateway_order_id"],
                            "amount": amount,
                        },
                        status_code=status.HTTP_201_CREATED,
                    )

                logger.warning("Order serializer validation failed", extra={"errors": serializer.errors, "user_id": user_id})
                return ResponseHandler.error(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

            except model_class.DoesNotExist:
                logger.warning("Invalid Plan Selected", extra={"planId": planId, "user_id": user_id})
                return ResponseHandler.error(
                    {"message": "Invalid Plan Selected"},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            except Exception as e:
                logger.exception("Cart order creation failed unexpectedly", extra={"user_id": user_id, "planId": planId})
                return ResponseHandler.error(
                    {"message": "Something went wrong while creating order"},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )



def capture_transaction_data(
        serializer_class,
        attempt_model,
        subscription_serializer_class,
        plan_model,
        order_model,
        request,
        AssessmentSession,
        Transaction
    ):
        try:
            logger.info("capture_transaction_data() TRIGGERED")

            order_id = request.data.get("razorpay_order_id")
            logger.info(
                "capture_transaction_data called",
                extra={"order_id": order_id, "user_id": getattr(request.user, "id", None)}
            )
            order = order_model.objects.get(gateway_order_id=order_id)
            plan_code = order.plan_type

            logger.debug(
                "Plan code retrieved",
                extra={"plan_code": plan_code, "order_id": order_id}
            )

            if plan_code == "ja_test":
                logger.info("Processing ja_test plan", extra={"user_id": request.user.id})
                pass

            # ASSESSMENT PLANS
            if plan_code in ["js_assesment", "js_test"]:
                user = request.user
                logger.info("Processing assessment plan",
                            extra={"plan_code": plan_code, "user_id": user.id})

                # delete old session
                deleted_count, _ = AssessmentSession.objects.filter(user=user).delete()
                logger.info("Deleted previous AssessmentSession",
                            extra={"user_id": user.id, "deleted_count": deleted_count})

                # create new session
                new_session = AssessmentSession.objects.create(
                    user=user,
                    order=order_id,
                    overall_score=0,
                    complete_percentage=0.00,
                    is_test_end=False,
                    status="IN_PROGRESS",
                )
                logger.info("New AssessmentSession created",
                            extra={"user_id": user.id, "session_id": new_session.id})

            # BASIC PLAN
            if plan_code == "ja_basic":
                user_id = request.user.id
                deleted_count, _ = attempt_model.objects.filter(user=user_id).delete()
                logger.info("Deleted attempts for ja_basic plan",
                            extra={"user_id": user_id, "deleted_count": deleted_count})


            request.data["plan"] = plan_model.objects.get(name=plan_code).id

            logger.debug("Plan ID assigned",
                        extra={"plan_code": plan_code, "user_id": request.user.id})

            order.status = "paid"
            order.save()

            logger.info(
                "Order updated to PAID",
                extra={"order_id": order_id, "user_id": request.user.id}
            )

            return serializer_handle(serializer_class, request)

        except order_model.DoesNotExist:
            logger.error("Order not found", extra={"order_id": order_id})
            return ResponseHandler.error("Order not found", status_code=status.HTTP_404_NOT_FOUND)

        except plan_model.DoesNotExist:
            logger.error("Plan not found", extra={"plan_code": plan_code})
            return ResponseHandler.error("Plan not found", status_code=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.exception(
                "Transaction data capture failed",
                extra={"user_id": getattr(request.user, "id", None)}
            )
            return ResponseHandler.error("Transaction capture failed",
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



def retake_test(model_class, subscription_model, serializer_class, attempt_model, request):
            try:
                plan_id = request.data.get("planId")
                assesment_session_id = request.data.get("assesment_session_id")
                subject_id = request.data.get("subject_id")
                user_id = getattr(request.user, "id", None)

                logger.info(
                    f"retake_test called",
                    extra={
                        "user_id": user_id,
                        "plan_id": plan_id,
                        "assesment_session_id": assesment_session_id,
                        "subject_id": subject_id,
                        "path": getattr(request, "path", None),
                    },
                )

                if not subject_id:
                    logger.warning("retake_test missing subject_id", extra={"user_id": user_id})
                    return ResponseHandler.error(
                        {"message": "subject_id is required"}, status_code=status.HTTP_400_BAD_REQUEST
                    )

                logger.info("Calling create_cart_order for retake_test", extra={"user_id": user_id, "subject_id": subject_id})
                return create_cart_order(model_class, subscription_model, serializer_class, request)

            except Exception as e:
                logger.exception("Something went wrong in retake_test", exc_info=e)
                return Response(
                    {"success": False, "message": "Something went wrong while initializing retake test"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )


def payment(order, transaction, OrderSerializer, request):
    try:
        logger.info("payment() called", extra={"path": getattr(request, "path", None), "user": getattr(request.user, "id", None)})

        orders = order.objects.select_related('user').all().order_by("-created_date")
        logger.debug("Fetched orders queryset", extra={"count_estimate": orders.count()})

        page_obj, count, total_pages = paginator(orders, request)
        serializer = OrderSerializer(page_obj, many=True)
        logger.debug("Serialized page_obj for orders", extra={"page_number": getattr(page_obj, "number", None)})

        total_amount = orders.aggregate(total=Sum("amount"))["total"] or 0
        logger.info("Computed total amount for orders", extra={"total_amount": total_amount})

        response_data = {
            "total_amount": total_amount,
            "pagination": {
                "total_count": count,
                "total_pages": total_pages,
                "current_page": page_obj.number,
            },
            "data": serializer.data,
        }

        logger.info("payment() completed successfully", extra={"total_count": count, "total_amount": total_amount})
        return JsonResponse(response_data, safe=False)

    except Exception as e:
        logger.exception("Unexpected error in payment()")
        raise


def generate_pdf(data):
    pdf_file = BytesIO()
    HTML(string=data).write_pdf(pdf_file)
    pdf_file.seek(0)
    return pdf_file


def check_user_subscription(subscription_model, user_id):
    try:
        subscription = subscription_model.objects.filter(user=user_id).first()
        if subscription:
            now = timezone.now()
            time_difference = now - subscription.created_date
            remaining_time = timedelta(days=30) - time_difference
            if remaining_time > timedelta(days=0):
                return True
        return False
    except Exception as e:
        logger.error(f"Failed to check subscription: {str(e)}")
        return ResponseHandler.error(status.HTTP_500_INTERNAL_SERVER_ERROR)


def job_status_update(model, serializer_class, request):
    if request.method in "POST":
        try:
            job_id = request.data.get("id")
            status_value = request.data.get("status")
            if not job_id or not status_value:
                return ResponseHandler.error(
                    JOB_STATUS_MISSING, status_code=status.HTTP_400_BAD_REQUEST
                )

            job = get_object_or_404(model, id=job_id)
            if job.user != request.user:
                return ResponseHandler.error(
                    ACCESS_REQUIRED, status_code=status.HTTP_400_BAD_REQUEST
                )
            serializer = serializer_class(job, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return ResponseHandler.success(
                    {"message": JOB_STATUS_UPDATED},
                    status_code=status.HTTP_201_CREATED,
                )
            return ResponseHandler.error(
                serializer.errors, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except:
            return ResponseHandler.error(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    elif request.method == "DELETE":
        return delete_handle(model, request)

def get_all_recruiter_details(model, serializer_class, request):
    try:
        # 🔹 Apply filters and search
        q_filters, filter_kwargs = filters(request) 
        recruiter_details = model.objects.select_related("user")

        if q_filters or filter_kwargs:
            recruiter_details = recruiter_details.filter(q_filters, **filter_kwargs) 

        if not recruiter_details.exists():
            return ResponseHandler.error(  # ✅ added return
                message=ERROR_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # 🔹 Sorting
        sort_fields = request.GET.getlist("sort[]", ["created_date"])
        recruiter_details = recruiter_details.annotate(
            first_name=F("user__first_name")
        ).order_by(*sort_fields)

        # 🔹 Pagination
        page_obj, count, total_pages = paginator(recruiter_details, request)
        serializer = serializer_class(page_obj, many=True)

        response_data = {
            "total_count": count,
            "total_pages": total_pages,
            "current_page": page_obj.number,
            "data": serializer.data,
        }
        return ResponseHandler.success(response_data, status_code=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in get_all_recruiter_details: {e}")
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

def get_all_job_seeker_details(model, serializer_class, request):
    try:
        # 🔹 Apply filters and search
        q_filters, filter_kwargs = filters(request) 

        job_seeker_details = model.objects.select_related('user')

        if q_filters or filter_kwargs:
            job_seeker_details = job_seeker_details.filter(q_filters, **filter_kwargs) 

        if not job_seeker_details.exists():
            return ResponseHandler.error(  # ✅ added return
                message=ERROR_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        sort_fields = request.GET.getlist("sort[]", ["created_date"])

        job_seeker_details = job_seeker_details.annotate(
            first_name=F('user__first_name')
        )

        job_seeker_details = job_seeker_details.order_by(*sort_fields)

        page_obj, count, total_pages = paginator(job_seeker_details, request)
        serializer = serializer_class(page_obj, many=True) 

        response_data = {
            "total_count": count,
            "total_pages": total_pages,
            "current_page": page_obj.number,
            "data": serializer.data,
        }
        return ResponseHandler.success(response_data, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"{e}")
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

def get_industry_type(obj):
    try:
        return obj.user.fi_fk_user.get_industry_type_display()
    except Exception:
            return None
        
def get_all_applied_applicant_details(job_apply_model, student_profile_model, serializer_class, request):
    try:
        job_id = request.data.get('job_id')
        applications = job_apply_model.objects.filter(job_id=job_id)
        student_ids = list(applications.values_list('student_id', flat=True))
        students = student_profile_model.objects.filter(user_id__in=student_ids)
        serializer = serializer_class(students, many=True, context={'job_id': job_id})
        page_obj, count, total_pages = paginator(students, request) 
        response_data = {
            "total_count": count,
            "total_pages": total_pages,
            "current_page": page_obj.number,
            "data": serializer.data,
        }
        return ResponseHandler.success(response_data, status_code=status.HTTP_200_OK)
    except Exception as e:
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def get_all_admin_details(model, serializer_class, request):
    try:
        # Filter only admin users (user_type = 3)
        admin_users = model.objects.filter(user_type=3)
        
        if not admin_users.exists():
            return ResponseHandler.error(
                message="No admin users found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Apply search filter if provided
        search_query = request.GET.get("search")
        if search_query:
            admin_users = admin_users.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(username__icontains=search_query)
            )

        # Apply sorting
        sort_fields = request.GET.getlist("sort[]", ["created_date"])
        admin_users = admin_users.order_by(*sort_fields)

        # Apply pagination
        page_obj, count, total_pages = paginator(admin_users, request)
        serializer = serializer_class(page_obj, many=True, context={"request": request})

        response_data = {
            "total_count": count,
            "total_pages": total_pages,
            "current_page": page_obj.number,
            "data": serializer.data,
        }
        return ResponseHandler.success(response_data, status_code=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in get_all_admin_details: {e}")
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )





def create_new_handler(serializer_class, request):
    try: 
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseHandler.success(serializer.data, status_code=status.HTTP_201_CREATED)
        return ResponseHandler.error(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    

def list_all_items_handler(model, serializer_class, request):
    try: 
        items = model.objects.all() 
        serializer = serializer_class(items, many=True) 
        return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)
    except Exception as e:
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

def get_item_by_id_handler(model,item_id, serializer_class, request):
    try: 
        instance = model.objects.get(id=item_id)
        if not instance:
            return ResponseHandler.error(
                RESPONSE_ERROR,
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = serializer_class(instance)
        return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)
    except Exception as e:
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

def delete_item_by_id_handler(model, request):
    try:
        id = request.data.get("id")
        instance = model.objects.get(id=id)
        instance.delete()
        return ResponseHandler.success([], status_code=status.HTTP_200_OK)
    except Exception as e:
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
def upload_question_image_handler(questionModel, questionsSerializer , request):
    if request.method == "POST":
        question_id = request.data.get("question_id")
        if not question_id:
            return Response({"error": "question_id is required"}, status=400)

        try:
            question = questionModel.objects.get(id=question_id)
        except questionModel.DoesNotExist:
            return Response({"error": "Question not found"}, status=404)

        # Replace old image if exists
        if "question_image" in request.FILES:
            if question.question_image:
                print("Got here:if2 ", question.question_image)
                question.question_image.delete(save=False)
            question.question_image = request.FILES["question_image"]

        question.save()
        serializer = questionsSerializer(question)
        return Response(serializer.data, status=200)

    elif request.method == "PATCH":
        question_id = request.data.get("question_id")
        if not question_id:
            return Response({"error": "question_id is required"}, status=400)

        try:
            question = questionModel.objects.get(id=question_id)
        except questionModel.DoesNotExist:
            return Response({"error": "Question not found"}, status=404)

        if question.question_image:
            question.question_image.delete(save=False)
            question.question_image = None
            question.save()

        return Response({"message": "Image removed"}, status=204)


def update_item_by_id_handler(model, serializer_class, request):
    try:
        id = request.data.get("id") 
        instance = model.objects.filter(id=id).first() 
        serializer = serializer_class(instance, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)
        
        return ResponseHandler.error(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def get_question_by_subject_id_handler(QuestionModel, QuestionsSerializer, subject_id, request):
    try:
        # Base queryset: filter by subject ID
        questions = QuestionModel.objects.filter(subject_id=subject_id)

        # Apply search filter if provided
        search_query = request.GET.get("search")
        if search_query:
            if search_query.isdigit():
                questions = questions.filter(id=int(search_query))
            else:
                # Optionally, handle non-numeric search queries (e.g., if you want to search by text later)
                pass

        # Handle sorting
        sort_fields = request.GET.getlist("sort[]", ["created_date"])
        mapped_sort_fields = []
        for field in sort_fields:
            if field.lstrip("-") == "created_date":  # check without leading '-'
                # preserve the '-' if present
                mapped_sort_fields.append(field.replace("created_date", "created_at"))
            else:
                mapped_sort_fields.append(field)

        questions = questions.order_by(*mapped_sort_fields)

        # Apply pagination
        page_obj, count, total_pages = paginator(questions, request)
        serializer = QuestionsSerializer(page_obj, many=True)

        # Prepare response
        response_data = {
            "total_count": count,
            "total_pages": total_pages,
            "current_page": page_obj.number,
            "data": serializer.data,
        }
        return ResponseHandler.success(response_data, status_code=status.HTTP_200_OK)

    except Exception as e:
        return ResponseHandler.error(str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    except Exception as e:
        logger.error(f"{e}")
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    

def create_question_handler(questions_serializer, request):
    try:
        data = request.data
        is_many = isinstance(data, list)

        serializer = questions_serializer(data=data, many=is_many)

        if serializer.is_valid():
            serializer.save()
            return ResponseHandler.success(
                serializer.data, 
                status_code=status.HTTP_201_CREATED
            )

        return ResponseHandler.error(
            serializer.errors, 
            status_code=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e: 
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def get_free_test_question_handler(QuestionModel, SubjectModel, AttemptSerializer,QuestionsSerializer, request):
    try:

        # Save payment details 
        subject_id = request.GET.get("subject_id")
        user_id = request.user.id

        # Create new attpemt
        data = {"user": user_id, "status": "IN_PROGRESS", "subject": subject_id}

        serializer = AttemptSerializer(data=data)

        if serializer.is_valid():
            attempt_response = serializer.save()
            attempt_id = attempt_response.id
        else:
            return ResponseHandler.error(
                serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        # Share questions
        # 1. Fetch subject
        subject = get_object_or_404(SubjectModel, id=subject_id) 

        # 2. Prepare base response (metadata)
        test_data = {
            "exam_name": subject.exam_name,
            "section_name": subject.section_name,
            "duration_minutes": subject.duration_minutes,
            "easy_question_count": subject.easy_question_count,
            "medium_question_count": subject.medium_question_count,
            "difficult_question_count": subject.difficult_question_count,
            "marks_correct": float(subject.marks_correct),
            "marks_incorrect": float(subject.marks_incorrect),
            "marks_unattempted": float(subject.marks_unattempted),
            "attempt_id": attempt_id
        }

        # 3. Collect random questions by difficulty_level
        all_questions = QuestionModel.objects.filter(subject_id=subject_id)
        serialized_questions = QuestionsSerializer(all_questions, many=True).data

        # 5. Add to response
        test_data["questions"] = serialized_questions

        return ResponseHandler.success(test_data, status_code=status.HTTP_200_OK)

    except Exception as e:
        print("Error in get_test_by_subject_id_handler:", str(e))
        return ResponseHandler.error(RESPONSE_ERROR, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_test_question_handler(QuestionModel, SubjectModel, AssessmentSessionModel, AttemptModel, AttemptSerializer,QuestionsSerializer, request):
    try:

        # Save payment details
        assesment_session_id = request.GET.get("assesment_session_id")
        subject_id = request.GET.get("subject_id")
        user_id = request.user.id

        if not assesment_session_id or not subject_id:
            return ResponseHandler.error(
                RESPONSE_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
            ) 
        
        assesment_details = AssessmentSessionModel.objects.get(id=assesment_session_id)

        if not assesment_details or not assesment_details.user_id == user_id:
            return ResponseHandler.error(
                RESPONSE_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        # prev_attempt = AttemptModel.objects.filter(subject=subject_id, user=user_id)
           
        # if prev_attempt:
        #     return ResponseHandler.error(
        #         ASSESMENT_TAKEN,
        #         status_code=status.HTTP_208_ALREADY_REPORTED,
        #     )
        
        # Now the user is valid to start test

        # Create new attpemt

        data = {"assessment_session": assesment_session_id, "user": user_id, "status": "IN_PROGRESS", "subject": subject_id}

        serializer = AttemptSerializer(data=data)

        if serializer.is_valid():
            attempt_response = serializer.save()
            attempt_id = attempt_response.id
        else:
            return ResponseHandler.error(
                serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        # Share questions
        # 1. Fetch subject
        subject = get_object_or_404(SubjectModel, id=subject_id) 

        # 2. Prepare base response (metadata)
        test_data = {
            "exam_name": subject.exam_name,
            "section_name": subject.section_name,
            "duration_minutes": subject.duration_minutes,
            "easy_question_count": subject.easy_question_count,
            "medium_question_count": subject.medium_question_count,
            "difficult_question_count": subject.difficult_question_count,
            "marks_correct": float(subject.marks_correct),
            "marks_incorrect": float(subject.marks_incorrect),
            "marks_unattempted": float(subject.marks_unattempted),
            "attempt_id": attempt_id
        }

        # 3. Collect random questions by difficulty_level
        def sample_questions(level: int, count: int):
            qs = QuestionModel.objects.filter(subject_id=subject_id, difficulty_level=level)
            qs_ids = list(qs.values_list("id", flat=True))

            if not qs_ids:
                return QuestionModel.objects.none()

            if count > len(qs_ids):
                count = len(qs_ids)

            selected_ids = random.sample(qs_ids, count)
            return QuestionModel.objects.filter(id__in=selected_ids)

        easy_qs = sample_questions(1, subject.easy_question_count)
        medium_qs = sample_questions(2, subject.medium_question_count)
        difficult_qs = sample_questions(3, subject.difficult_question_count)

        # 4. Serialize
        all_questions = easy_qs | medium_qs | difficult_qs
        serialized_questions = QuestionsSerializer(all_questions, many=True).data

        # 5. Add to response
        test_data["questions"] = serialized_questions

        return ResponseHandler.success(test_data, status_code=status.HTTP_200_OK)

    except Exception as e:
        print("Error in get_test_by_subject_id_handler:", str(e))
        return ResponseHandler.error(RESPONSE_ERROR, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def submit_test_handler(AttemptModel, AttemptAnswerModel, Question, attempt_id, request):
    try:
        # is_completed = request.data.get("is_completed")

        # # Check if test is compelted already then no change
        # if is_completed == True:
        #     return ResponseHandler.error(
        #         RESPONSE_ERROR,
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #     )

        user_id = request.user.id
        attempt_details = AttemptModel.objects.get(id=attempt_id)

        # check authentication for the user
        if not attempt_details.user_id == user_id:
            return ResponseHandler.error(
                RESPONSE_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        subject_correct_score = attempt_details.subject.marks_correct
        subject_incorrect_score = attempt_details.subject.marks_incorrect

        # questionId_currentQIndex: answer_status
        answers = request.data.get("answers")
        result = {}
 
        for question, answer in answers.items():
 
            question_key, question_value = question.split("_") 
            answer_key, answer_value = answer.split("_") 
            result[int(question_key)] = int(answer_value)
 

        option_mapping = {
            0: "OPTION_1",
            1: "OPTION_2",
            2: "OPTION_3",
            3: "OPTION_4"
        }


        #  change value according to subject 
        correct_answer_score = 1
        incorrect_answer_score = 0

        # Prepare the list of QuestionAnswer instances to insert
        question_answers = []
        for question_id, option_value in result.items():
            score = incorrect_answer_score
            question_obj = Question.objects.get(id=question_id)
            selected_option = option_mapping.get(option_value, "OPTION_1")
            is_correct = (selected_option == question_obj.correct_option)

            if is_correct:
                score = correct_answer_score

            question_answer = AttemptAnswerModel(
                attempt=attempt_details,
                question=question_obj,
                selected_option=option_mapping.get(option_value, "OPTION_1"),  # Default to OPTION_1 if not found
                is_correct=is_correct,
                score=score,
            )
            question_answers.append(question_answer)

        AttemptAnswerModel.objects.bulk_create(question_answers)

        return ResponseHandler.success(
            {
                "success": "submited sucessfully",
            }, 
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return ResponseHandler.error(
            RESPONSE_ERROR, 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def create_assesment_session(payment_id, user_id, assesment_session_serializer):
    try:
        data = {"payment_id": payment_id, "user": user_id, "overall_score": 0, "complete_percentage": 0.00, "status": "IN_PROGRESS", "is_test_end": False}


        serializer = assesment_session_serializer(data=data)

        if serializer.is_valid():
            serializer.save() 
            return {
                "success": True,
                "data": serializer.data
            }
 
        return {
            "success": False,
            "data": serializer.errors
        }

    except Exception as e: 
        return {
            "success": False,
            "data": RESPONSE_ERROR
        }


def create_payment_handler(payment_serializer, assesment_session_serializer, request):
    try:
        data = request.data
        serializer = payment_serializer(data=data)

        if serializer.is_valid():
            serializer.save()

            if serializer.data["status"] == "SUCCESS":
                create_assesment_session(serializer.data["id"], request.user.id, assesment_session_serializer)
    
            return ResponseHandler.success(
                serializer.data, 
                status_code=status.HTTP_201_CREATED
            )

        return ResponseHandler.error(
            serializer.errors, 
            status_code=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e: 
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def update_payment_by_id_handler(model, serializer_class, assesment_session_serializer, request):
    try:
        id = request.data.get("id") 
        instance = model.objects.filter(id=id).first() 
        serializer = serializer_class(instance, data=request.data, partial=True)

        print("Status: ", request.data.get("status"))
        if(request.data.get("status") == "SUCCESS"):
            print("Request got inside success")
            create_assesment_session(instance.id, request.user.id, assesment_session_serializer)

        if serializer.is_valid():
            serializer.save()
            return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)
        
        return ResponseHandler.error(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def get_user_assesment_session_handler(user_model, assesment_session_model, serializer_class, pk, request): 
    try: 
        user_instance = user_model.objects.get(**pk)
        assesment_sessions = assesment_session_model.objects.filter(user_id=user_instance.id)
 
        assesment_data = serializer_class(assesment_sessions, many=True).data
        return ResponseHandler.success(assesment_data, status_code=status.HTTP_200_OK)

    except user_model.DoesNotExist:
        return ResponseHandler.error(
            "User not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print("Error: ", e)
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def get_all_assesment_attempts_handler(user_model, assesment_session_model, serializer_class, pk, assesment_session_id, request): 
    try: 
        user_instance = user_model.objects.get(**pk)
 
        assesment_sessions = assesment_session_model.objects.filter(user_id=user_instance.id, assessment_session=assesment_session_id)
 
        assesment_data = serializer_class(assesment_sessions, many=True).data
        return ResponseHandler.success(assesment_data, status_code=status.HTTP_200_OK)

    except user_model.DoesNotExist:
        return ResponseHandler.error(
            "User not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    except Exception as e:
        print("Error: ", e)
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# def get_resluts_handler(attempt_model, attempt_answer_model, attempt_answer_serializer, attempt_id, request): 
#     try:
#         attempt = attempt_model.objects.get(id=attempt_id)
#         print("Attempt: " , attempt.subject)
#         attempt_answers = attempt_answer_model.objects.filter(attempt=attempt_id)

#         serializer = attempt_answer_serializer(attempt_answers, many=True)
#         print("Answers: ", serializer.data)
#         # Count answers
#         total_answers = attempt_answers.count()
#         print("Total answers: ", total_answers)
#         # Sum score field
#         total_score = sum(ans.score for ans in attempt_answers)
#         print("Total score: ", total_score)
#         response_data = {
#             "attempt": {
#                 "id": attempt.id,
#                 "subject": attempt.subject,
#                 "status": attempt.status,
#             },
#             "answers": serializer.data,
#             "total_answers": total_answers,
#             "total_score": total_score
#         }

#         return ResponseHandler.success(response_data, status_code=status.HTTP_200_OK)

#     except Exception as e:
#         print("Error in get_resluts_handler:", e)
#         return ResponseHandler.error(
#             RESPONSE_ERROR,
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )



def get_results_handler(attempt_model, attempt_answer_model, attempt_id, request): 
    try:

        # Get attempt id
        attempt = attempt_model.objects.get(id=attempt_id)
        if attempt.score is not None :
            return ResponseHandler.success(
                {
                    "assesment_total": attempt.maximum_possible_score,
                    "total_marks_scored": attempt.score,
                    "assesment_session_id": getattr(attempt.assessment_session, "id", 0)
                },
                status_code=status.HTTP_200_OK
            )

        attempt_answers = attempt_answer_model.objects.filter(attempt=attempt_id)

        # get the score
        total_answers = attempt_answers.count()
        TE = getattr(attempt.subject, "easy_question_count", 0)
        TM = getattr(attempt.subject, "medium_question_count", 0)
        TD = getattr(attempt.subject, "difficult_question_count", 0)
        NA = getattr(attempt.subject, "marks_unattempted", 0)
        CA = getattr(attempt.subject, "marks_correct", 0)
        subject_id =  getattr(attempt.assessment_session, "id", 0)

        total_questions = TE + TM + TD
        not_answered_calc = (total_questions - total_answers) * NA

        assesment_total = total_questions * CA

        total_answer_sum = total_answers * CA

        total_marks_scored = not_answered_calc + total_answer_sum

        # store the score in database
        attempt.score = total_marks_scored
        attempt.maximum_possible_score = assesment_total
        attempt.save()

        response_data = {
            "assesment_total ": assesment_total,
            "total_marks_scored": total_marks_scored,
            "assesment_session_id" : subject_id
        }

        return ResponseHandler.success(response_data, status_code=status.HTTP_200_OK)

    except Exception as e:
        print("Error in get_resluts_handler:", e)
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 

def get_payment_by_userid_handler(PaymentModel, PaymentSerializer, user_id, request):
    try:
        payments = PaymentModel.objects.filter(user_id=user_id)
        serializer = PaymentSerializer(payments, many=True)
        return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)
    except Exception as e:
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
def get_payment_by_id_handler(PaymentModel, PaymentSerializer, item_id, request):
    try:
        instance = PaymentModel.objects.get(id=item_id)
        if not instance:
            return ResponseHandler.error(
                RESPONSE_ERROR,
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = PaymentSerializer(instance)
        return ResponseHandler.success(serializer.data, status_code=status.HTTP_200_OK)
    except Exception as e:
        return ResponseHandler.error(
            RESPONSE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    



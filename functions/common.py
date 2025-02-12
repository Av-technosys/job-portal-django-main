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
    except Exception as e:
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


def get_customize_handler(model, serializer_class, pk, request):
    try:
        instances = model.objects.filter(**pk)
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
            q_filters = Q(company_name__icontains=filter_result) | Q(
                company_description__icontains=filter_result
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

    owner_filters = {}
    if request.data.get("owner"):
        owner_filters["user_id__in"] = request.data.get("owner")

    try:
        if not q_filters and not filter_kwargs and not owner_filters:
            instances = model_class.objects.all()

        else:
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
        ResponseHandler.api_exception_error()


def create_cart_order(model_class, subscription_model, serializer_class, request):
    try:
        user_id = request.user.id
        planId = request.data.get("planId")
        amount = model_class.objects.get(name=planId).price
        is_subscribed = check_user_subscription(subscription_model, user_id)
        if is_subscribed:
            return ResponseHandler.error(
                RESUBSCRIBE_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        razorpay_order = get_razorpay_order(
            {
                "amount": amount * 100,
                "currency": "INR",
                "receipt": f"order_{user_id}_{int(time.time())}",
            }
        )

        razorpay_order["gateway_order_id"] = razorpay_order["id"]
        razorpay_order["user"] = user_id
        razorpay_order["plan_type"] = planId

        serializer = serializer_class(data=razorpay_order)
        if serializer.is_valid():
            serializer.save()
            # Only return gateway_order_id in response
            return ResponseHandler.success(
                {"gateway_order_id": razorpay_order["gateway_order_id"]},
                status_code=status.HTTP_201_CREATED,
            )
        return ResponseHandler.error(
            serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        logger.error(f"Cart order creation failed: {str(e)}")
        return ResponseHandler.error(status.HTTP_500_INTERNAL_SERVER_ERROR)


def capture_transaction_data(
    serializer_class,
    subscription_model,
    subscription_serializer_class,
    plan_model,
    order_model,
    request,
):
    try:
        order_id = request.data.get("razorpay_order_id")
        plan_code = order_model.objects.get(gateway_order_id=order_id).plan_type
        request.data["plan"] = plan_model.objects.get(name=plan_code).id
        user_id = request.user.id
        is_subscribed = check_user_subscription(subscription_model, user_id)
        if is_subscribed:
            return ResponseHandler.error(
                RESUBSCRIBE_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        serializer_handle(subscription_serializer_class, request)
        return serializer_handle(serializer_class, request)
    except Exception as e:
        logger.error(f"Transaction data capture failed: {str(e)}")
        return ResponseHandler.error(status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        recruiter_details = model.objects.all()
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




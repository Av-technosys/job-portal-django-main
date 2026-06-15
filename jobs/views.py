from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import *
from assessment.models import Attempt
from functions.cache import get_or_set_response_cache
from handlers.common import *
from user_profiles.models import StudentProfile
from user_profiles.serializers import ListCandidateSerializer, StudentProfileSerializer
from handlers.permissions import IsRecruiter, IsJobSeeker


@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, IsRecruiter])
def job_details_api_view(request):
    return request_handler(JobInfo, JobCombinedSerializer, request)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsJobSeeker])
def apply_job(request):
    return job_apply_handler(JobApplySerializer, JobInfo, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_jobs(request):
    return get_or_set_response_cache(
        request,
        "list_jobs",
        lambda: get_job_listing(JobInfo, JobSeekerListingViewSerializer, request),
        vary_by_user=True,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsRecruiter])
def my_posted_jobs(request):
    request.data["owner"] = [request.user.id]
    return filter_search_handler(JobInfo, JobPostedListSerializer, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def submitted_jobs_application(request):
    return application_handler(
        JobApply,
        JobApplySerializer,
        StudentProfile,
        StudentProfileSerializer,
        request,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_submitted_jobs(request):
    return application_handler(
        JobApply,
        JobApplySerializer,
        JobInfo,
        AppliedJobListViewSerializer,
        request,
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsRecruiter])
def application_status(request):
    return handle_application_status(JobApply, JobApplySerializer, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsRecruiter])
def application_assessment_scores(request, application_id):
    application = JobApply.objects.filter(
        id=application_id,
        owner=request.user,
    ).first()

    if not application:
        return ResponseHandler.error(
            ERROR_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    attempts = Attempt.objects.filter(
        user_id=application.student_id,
    ).select_related("subject", "assessment_session").order_by("-updated_at", "-id")

    response_data = []

    for attempt in attempts:
        assessment_total = attempt.maximum_possible_score
        total_marks_scored = attempt.score

        if total_marks_scored is None or assessment_total is None:
            total_answers = attempt.answers.count()
            total_questions = (
                attempt.subject.easy_question_count
                + attempt.subject.medium_question_count
                + attempt.subject.difficult_question_count
            )
            not_answered_calc = (
                total_questions - total_answers
            ) * attempt.subject.marks_unattempted
            assessment_total = total_questions * attempt.subject.marks_correct
            total_marks_scored = not_answered_calc + (
                total_answers * attempt.subject.marks_correct
            )

            attempt.score = total_marks_scored
            attempt.maximum_possible_score = assessment_total
            attempt.save(update_fields=["score", "maximum_possible_score", "updated_at"])

        percentage = 0
        if assessment_total:
            percentage = (total_marks_scored / assessment_total) * 100

        response_data.append(
            {
                "id": attempt.id,
                "attempt_id": attempt.id,
                "subject_id": attempt.subject_id,
                "subject_name": attempt.subject.exam_name,
                "section_name": attempt.subject.section_name,
                "score": total_marks_scored,
                "total_marks_scored": total_marks_scored,
                "assessment_total": assessment_total,
                "assesment_total": assessment_total,
                "maximum_possible_score": assessment_total,
                "percentage": percentage,
                "assessment_session_id": getattr(attempt.assessment_session, "id", 0),
                "assesment_session_id": getattr(attempt.assessment_session, "id", 0),
                "submit_time": attempt.submit_time,
                "created_at": attempt.created_at,
                "updated_at": attempt.updated_at,
                "status": attempt.status,
            }
        )

    return ResponseHandler.success(response_data, status_code=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def chat(request, application_id):
    return message_handler(CommunicationSerializer, request, application_id)


@api_view(["POST", "DELETE", "GET"])
@permission_classes([IsAuthenticated, IsJobSeeker])
def save_job(request):
    return job_save_handler(
        JobSaveSerializer,
        SavedJobsJobSeekerListingViewSerializer,
        JobSaved,
        JobInfo,
        request,
    )


@api_view(["POST", "DELETE", "GET"])
@permission_classes([IsAuthenticated, IsRecruiter])
def save_cadidate(request):
    return candidate_save_handler(
        CandidateSaveSerializer,
        ListCandidateSerializer,
        CandidateSaved,
        StudentProfile,
        request,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def summary_view(request):
    return summary_counter_handler(JobApply, JobSaved, CandidateSaved, JobInfo, request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def job_details_by_id(request, job_id):
    return job_details_by_job_id(JobInfo, job_id, JobDetailsCombinedSerializer, request)


@api_view(["DELETE", "POST"])
@permission_classes([IsAuthenticated, IsRecruiter])
def job_status_by_recruiter(request):
    return job_status_update(JobInfo, JobStatusUpdateSerializer, request)

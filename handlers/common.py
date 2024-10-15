from functions.common import *
from constants.errors import *


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

def post_filter_handler(request):
    filters = {}
    if request.data.get('education'):
        filters['user__academicqualification__specialization__icontains'] = request.data.get('education')

    if request.data.get('location'):
        filters['city__icontains'] = request.data.get('location')

    if request.data.get('experience'):
        filters['experience__gte'] = request.data.get('experience')

    if request.data.get('skills'):
        filters['user__skillset__skill_name__icontains'] = request.data.get('skills')

    if request.data.get('salary_expectations'):
        filters['expecting_salary__lte'] = request.data.get('salary_expectations')
        
    return filters
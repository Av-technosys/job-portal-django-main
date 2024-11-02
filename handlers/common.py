def post_filter_handler(request):
    filters = {}
    if request.data.get("education"):
        filters["user__academicqualification__specialization__icontains"] = (
            request.data.get("education")
        )

    if request.data.get("location"):
        filters["city__icontains"] = request.data.get("location")

    if request.data.get("experience"):
        filters["experience__gte"] = request.data.get("experience")

    if request.data.get("skills"):
        filters["user__skillset__skill_name__icontains"] = request.data.get("skills")

    if request.data.get("salary_expectations"):
        filters["expecting_salary__lte"] = request.data.get("salary_expectations")

    return filters

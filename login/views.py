from django.shortcuts import render

from django.http import HttpResponse


def login(request):
    return HttpResponse("You have called the login API call", request)
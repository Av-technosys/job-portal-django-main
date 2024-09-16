from django.shortcuts import render

from django.http import HttpResponse


def register(request):
    return HttpResponse("You have called the register API call", request)
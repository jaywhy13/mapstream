from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import render_to_response

def index(request):
    return render_to_response('static/map/Main.html')


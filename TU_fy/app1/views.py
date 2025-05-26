#functions wie get blablabla

from django.shortcuts import render, redirect

from app1.models import Request
from template import *

def index(request):
    artist= Request.objects.all()
    return render(request, "index.html" ,{'artist': artist} )



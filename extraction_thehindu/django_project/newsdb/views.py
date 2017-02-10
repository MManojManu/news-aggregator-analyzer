from __future__ import print_function
from __future__ import unicode_literals
from django.http import HttpResponse


def index(request):
    return HttpResponse("Welcome news-aggregator-analyzer.")


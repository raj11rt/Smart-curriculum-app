from django.http import HttpResponse


def home(request):
    return HttpResponse("Smart Curriculum App: Backend is working!")


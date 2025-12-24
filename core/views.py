from django.shortcuts import render
from .models import TimetableEntry


def home(request):
    entries = TimetableEntry.objects.all().order_by("day", "period")
    return render(request, "core/timetable.html", {"entries": entries})

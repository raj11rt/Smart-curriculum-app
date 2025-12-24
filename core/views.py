import datetime
from django.shortcuts import render
from .models import TimetableEntry


def home(request):
    entries = TimetableEntry.objects.all().order_by("day", "period")
    return render(request, "core/timetable.html", {"entries": entries})


def today_schedule(request):
    weekday_map = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }
    today_name = weekday_map[datetime.date.today().weekday()]
    entries = (
        TimetableEntry.objects.filter(day=today_name)
        .order_by("period")
    )
    context = {
        "day": today_name,
        "entries": entries,
    }
    return render(request, "core/today_schedule.html", context)

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
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from .models import Student, TimetableEntry, Attendance
import datetime


@require_POST
def mark_attendance(request):
    student_id = request.POST.get("student_id")
    timetable_id = request.POST.get("timetable_id")
    date_str = request.POST.get("date")
    method = request.POST.get("method", "QR")

    if not (student_id and timetable_id and date_str):
        return HttpResponseBadRequest("Missing required parameters")

    try:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponseBadRequest("Invalid date format, expected YYYY-MM-DD")

    try:
        student = Student.objects.get(id=student_id)
        timetable_entry = TimetableEntry.objects.get(id=timetable_id)
    except (Student.DoesNotExist, TimetableEntry.DoesNotExist):
        return HttpResponseBadRequest("Student or timetable entry not found")

    attendance, created = Attendance.objects.update_or_create(
        student=student,
        timetable_entry=timetable_entry,
        date=date,
        defaults={"method": method, "present": True},
    )

    if created:
        message = "Attendance created successfully."
    else:
        message = "Attendance updated successfully."

    return HttpResponse(
        f"{message} Student: {student.roll_no}, Class: {timetable_entry.subject}, Date: {date}."
    )

import datetime
import io
import qrcode

from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import TimetableEntry, Student, Attendance


@login_required
def home(request):
    if request.user.is_staff:
        return redirect("teacher_dashboard")
    else:
        return redirect("student_dashboard")


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
    entries = TimetableEntry.objects.filter(day=today_name).order_by("period")
    context = {
        "day": today_name,
        "entries": entries,
    }
    return render(request, "core/today_schedule.html", context)


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

    return JsonResponse(
        {
            "status": "created" if created else "updated",
            "student_roll_no": student.roll_no,
            "subject": timetable_entry.subject,
            "date": str(date),
            "method": method,
        }
    )
def class_qr(request, timetable_id):
    timetable_entry = get_object_or_404(TimetableEntry, id=timetable_id)

    base_url = request.build_absolute_uri("/")[:-1]
    data = f"{base_url}/mark-attendance-demo/?timetable_id={timetable_entry.id}&date={datetime.date.today()}"

    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
# (csrf_exempt already from django if not, import it)

@csrf_exempt
def mark_attendance_demo_get(request):
    """
    TEMP demo: mark attendance via GET for a fixed student (id=1).
    Replace later with proper auth/mobile app.
    """
    if request.method != "GET":
        return HttpResponseBadRequest("Use GET only for demo")

    student_id = request.GET.get("student_id", "1")  # default demo student
    timetable_id = request.GET.get("timetable_id")
    date_str = request.GET.get("date")

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
        defaults={"method": "QR", "present": True},
    )

    return JsonResponse(
        {
            "status": "created" if created else "updated",
            "student_roll_no": student.roll_no,
            "subject": timetable_entry.subject,
            "date": str(date),
            "method": "QR",
            "demo": True,
        }
    )
from django.utils import timezone
from datetime import timedelta

@login_required
def teacher_dashboard(request):
    classes = TimetableEntry.objects.filter(
        teacher=request.user
    ).order_by("day", "period")

    recent_attendance = Attendance.objects.filter(
        timetable_entry__teacher=request.user,
        marked_at__gte=timezone.now() - timedelta(days=7),  # <— change here
    ).select_related("student", "timetable_entry").order_by("-marked_at")[:20]

    context = {
        "classes": classes,
        "recent_attendance": recent_attendance,
    }
    return render(request, "core/teacher_dashboard.html", context)

@login_required
def student_dashboard(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return render(request, "core/student_dashboard.html", {
            "entries": [],
            "subject_stats": [],
            "overall_percent": 0,
            "error": "No student profile found. Contact admin."
        })
    
    entries = TimetableEntry.objects.all().order_by("day", "period")
    subject_stats = student.attendance_by_subject()
    overall_percent = student.overall_attendance_percent()
    
    suggestions = []
    low_attendance_subjects = [s for s in subject_stats if s['percent'] < 75]
    
    if low_attendance_subjects:
        low_sub = low_attendance_subjects[0]  # worst subject first
        suggestions.append({
            'icon': '📚',
            'subject': low_sub['subject'],
            'text': f'Review {low_sub["subject"]} (only {low_sub["percent"]}% attendance)',
        })
    
    upcoming_classes = entries[:3]  # next 3 classes
    for cls in upcoming_classes:
        suggestions.append({
            'icon': '🎯',
            'subject': cls.subject,
            'text': f'Practice 2 problems for {cls.subject} class',
        })

    context = {
        "entries": entries,
        "subject_stats": subject_stats,
        "overall_percent": overall_percent,
    }
    return render(request, "core/student_dashboard.html", context)

import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def export_class_attendance(request, timetable_id):
    from django.shortcuts import get_object_or_404
    timetable = get_object_or_404(TimetableEntry, id=timetable_id, teacher=request.user)

    records = (
        Attendance.objects
        .filter(timetable_entry=timetable)
        .select_related("student")
        .order_by("student__roll_no", "marked_at")  # use marked_at
    )

    response = HttpResponse(content_type="text/csv")
    filename = f"attendance_{timetable.subject}_{timetable.day}_P{timetable.period}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(["Roll No", "Student", "Date & Time", "Present"])  # use "Present"
    
    for a in records:
        writer.writerow([
            a.student.roll_no,
            a.student.user.get_full_name() or a.student.user.username,
            a.marked_at.strftime("%Y-%m-%d %H:%M"),  # use marked_at
            "Yes" if a.present else "No",  # use present boolean
        ])

    return response

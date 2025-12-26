from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("today/", views.today_schedule, name="today_schedule"),
    path("mark-attendance/", views.mark_attendance, name="mark_attendance"),
    path("mark-attendance-demo/", views.mark_attendance_demo_get, name="mark_attendance_demo"),
    path("class/<int:timetable_id>/qr/", views.class_qr, name="class_qr"),

    path("teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("student/", views.student_dashboard, name="student_dashboard"),
]

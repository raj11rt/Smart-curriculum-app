from django.contrib import admin
from .models import Student, TimetableEntry, Attendance


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("roll_no", "user", "branch", "semester")
    search_fields = ("roll_no", "user__username", "user__first_name", "user__last_name")


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ("day", "period", "subject", "teacher", "room")
    list_filter = ("day", "teacher")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "timetable_entry", "date", "method", "present")
    list_filter = ("date", "method", "present")


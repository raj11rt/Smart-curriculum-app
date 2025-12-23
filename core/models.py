from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_no = models.CharField(max_length=20, unique=True)
    branch = models.CharField(max_length=50, blank=True)
    semester = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.roll_no} - {self.user.get_full_name() or self.user.username}"


class TimetableEntry(models.Model):
    day = models.CharField(max_length=10)  # e.g. Monday
    period = models.IntegerField()         # 1,2,3...
    subject = models.CharField(max_length=100)
    room = models.CharField(max_length=20, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="classes")

    def __str__(self):
        return f"{self.day} P{self.period} - {self.subject}"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    timetable_entry = models.ForeignKey(TimetableEntry, on_delete=models.CASCADE)
    date = models.DateField()
    marked_at = models.DateTimeField(auto_now_add=True)
    method = models.CharField(
        max_length=20,
        choices=(
            ("QR", "QR"),
            ("BT", "Bluetooth"),
            ("WIFI", "WiFi"),
            ("FACE", "Face"),
        ),
        default="QR",
    )
    present = models.BooleanField(default=True)

    class Meta:
        unique_together = ("student", "timetable_entry", "date")

    def __str__(self):
        return f"{self.student.roll_no} - {self.timetable_entry} - {self.date}"


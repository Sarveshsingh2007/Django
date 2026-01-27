from django.db import models
from django.utils import timezone
from students.models import Student
from subjects.models import Subject

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_code = models.CharField(max_length=2)
    date = models.DateField()
    present = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'subject', 'date')

    def can_edit(self):
        return timezone.now() <= self.created_at + timezone.timedelta(hours=24)

from django.db import models
from django.conf import settings
from subjects.models import Subject

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    CLASS_CHOICES = (
        ('11', 'Class 11'),
        ('12', 'Class 12'),
    )

    class_code = models.CharField(max_length=2, choices=CLASS_CHOICES)
    subjects = models.ManyToManyField(Subject)

    def __str__(self):
        return self.user.username

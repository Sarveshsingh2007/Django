from django.db import models
from django.conf import settings
from subjects.models import Subject

class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    CLASSES = (
        ('11', 'Class 11'),
        ('12', 'Class 12'),
    )

    classes = models.ManyToManyField(
        'TeacherClass',
        related_name='teachers'
    )

    def __str__(self):
        return self.user.username


class TeacherClass(models.Model):
    code = models.CharField(max_length=2, choices=Teacher.CLASSES, unique=True)

    def __str__(self):
        return f"Class {self.code}"

from django.db import models
from django.conf import settings
from subjects.models import Subject


class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject)


    def __str__(self):
        return self.user.username
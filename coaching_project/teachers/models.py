from django.db import models
from django.conf import settings
from subjects.models import Subject


class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teaching_class = models.CharField(max_length=20)


    def __str__(self):
        return self.user.username
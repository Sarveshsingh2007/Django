from django.db import models

# Create your models here.

class Note(models.Model):
    subject = models.CharField(max_length=20)
    title = models.CharField(max_length=150)
    description = models.TextField()
    file = models.FileField(upload_to='notes_files/')
    created_at = models.DateTimeField(auto_now_add=True)
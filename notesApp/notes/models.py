from django.db import models

class Note(models.Model):
    subject = models.CharField(max_length=20,default="General")
    title = models.CharField(max_length=150)
    description = models.TextField()
    file = models.FileField(upload_to='notes_files/',blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

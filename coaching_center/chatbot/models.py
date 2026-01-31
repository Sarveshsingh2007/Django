from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Session {self.session_id} - {self.user if self.user else 'Anonymous'}"
    
    class Meta:
        ordering = ['-created_at']


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField()
    is_bot = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{'Bot' if self.is_bot else 'User'}: {self.message[:50]}"
    
    class Meta:
        ordering = ['timestamp']


class FAQ(models.Model):
    CATEGORY_CHOICES = (
        ('general', 'General'),
        ('admission', 'Admission'),
        ('fees', 'Fees'),
        ('attendance', 'Attendance'),
        ('timetable', 'Timetable'),
        ('notes', 'Notes'),
        ('teachers', 'Teachers'),
        ('other', 'Other'),
    )
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    question = models.TextField()
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.category} - {self.question[:50]}"
    
    class Meta:
        ordering = ['category', 'question']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.username} ({self.user_type})"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Teacher(models.Model):
    CLASS_CHOICES = (
        ('11', 'Class 11th'),
        ('12', 'Class 12th'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    image = models.ImageField(upload_to='teacher_images/', default='default.jpg')
    name = models.CharField(max_length=200)
    teacher_id = models.CharField(max_length=20, unique=True, blank=True)
    classes = models.CharField(max_length=50)  # Stores comma-separated class values
    subjects = models.ManyToManyField(Subject, related_name='teachers')
    mobile = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^\d{10}$', message='Enter a valid 10-digit mobile number')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.teacher_id:
            # Generate teacher ID: T001, T002, etc.
            last_teacher = Teacher.objects.all().order_by('id').last()
            if last_teacher:
                last_id = int(last_teacher.teacher_id[1:])
                self.teacher_id = f'T{str(last_id + 1).zfill(3)}'
            else:
                self.teacher_id = 'T001'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.teacher_id})"


class Student(models.Model):
    CLASS_CHOICES = (
        ('11', 'Class 11th'),
        ('12', 'Class 12th'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    image = models.ImageField(upload_to='student_images/', default='default.jpg')
    name = models.CharField(max_length=200)
    student_id = models.CharField(max_length=20, unique=True, blank=True)
    class_name = models.CharField(max_length=2, choices=CLASS_CHOICES)
    subjects = models.ManyToManyField(Subject, related_name='students')
    mobile = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^\d{10}$', message='Enter a valid 10-digit mobile number')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.student_id:
            # Generate student ID: S001, S002, etc.
            last_student = Student.objects.all().order_by('id').last()
            if last_student:
                last_id = int(last_student.student_id[1:])
                self.student_id = f'S{str(last_id + 1).zfill(3)}'
            else:
                self.student_id = 'S001'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.student_id})"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    marked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'subject', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student.name} - {self.subject.name} - {self.date}"


class Notes(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='notes')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    topic = models.CharField(max_length=200)
    file = models.FileField(upload_to='notes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name_plural = 'Notes'
    
    def __str__(self):
        return f"{self.subject.name} - {self.topic}"


class Fee(models.Model):
    MONTH_CHOICES = (
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    )
    
    STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('overdue', 'Overdue'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    month = models.CharField(max_length=20, choices=MONTH_CHOICES)
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    paid_date = models.DateField(null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'month', 'year']
        ordering = ['-year', '-id']
    
    def __str__(self):
        return f"{self.student.name} - {self.month} {self.year}"


class TimeTable(models.Model):
    DAY_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    )
    
    TIME_CHOICES = (
        ('3:30-4:30 PM', '3:30-4:30 PM'),
        ('4:30-5:30 PM', '4:30-5:30 PM'),
    )
    
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    time_slot = models.CharField(max_length=20, choices=TIME_CHOICES)
    class_name = models.CharField(max_length=2, choices=Student.CLASS_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['day', 'time_slot', 'class_name']
        ordering = ['day', 'time_slot']
    
    def __str__(self):
        return f"{self.day} {self.time_slot} - Class {self.class_name} - {self.subject.name}"
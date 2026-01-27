from django.shortcuts import render
from .models import Student
from attendance.models import Attendance
from accounts.decorators import student_required
from django.contrib.auth.decorators import login_required
from subjects.models import Subject

@login_required
def student_dashboard(request):
    student = request.user.student
    subject_data = []

    for subject in student.subjects.all():
        total = Attendance.objects.filter(
            student=student,
            subject=subject
        ).count()

        present = Attendance.objects.filter(
            student=student,
            subject=subject,
            present=True
        ).count()

        percentage = int((present / total) * 100) if total > 0 else 0

        subject_data.append({
            'subject': subject.name,
            'total': total,
            'present': present,
            'percentage': percentage
        })

    return render(request, 'students/dashboard.html', {
        'subject_data': subject_data
    })

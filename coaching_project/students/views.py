from django.shortcuts import render
from .models import Student
from attendance.models import Attendance
from accounts.decorators import student_required

@student_required
def student_dashboard(request):
    student = Student.objects.get(user=request.user)

    subject_data = []

    for subject in student.subjects.all():
        total = Attendance.objects.filter(
            student=student, subject=subject
        ).count()

        present = Attendance.objects.filter(
            student=student, subject=subject, is_present=True
        ).count()

        percentage = (present / total) * 100 if total > 0 else 0

        subject_data.append({
            'subject': subject.name,
            'total': total,
            'present': present,
            'percentage': round(percentage, 2)
        })

    return render(request, 'students/dashboard.html', {
        'subject_data': subject_data
    })

from django.shortcuts import redirect
from .models import Attendance
from students.models import Student




def mark_attendance(request, subject_id):
    if request.method == 'POST':
        for key in request.POST:
            if key.startswith('student_'):
                student_id = key.split('_')[1]
                Attendance.objects.create(
                    student_id=student_id,
                    subject_id=subject_id,
                    is_present=True
                )
    return redirect('teacher_dashboard')
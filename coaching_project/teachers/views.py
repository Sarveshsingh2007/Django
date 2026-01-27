from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from subjects.models import Subject
from students.models import Student
from attendance.models import Attendance


@login_required
def teacher_dashboard(request):
    teacher = request.user.teacher

    students = None
    can_edit = True

    # GET parameters (from filter form)
    selected_date = request.GET.get('date')
    selected_class = request.GET.get('class_code')

    subject_id = teacher.subject.id

    # LOAD STUDENTS (GET request)
    if selected_date and selected_class:
        students = Student.objects.filter(
            subjects__id=subject_id,
            class_code=selected_class
        )

        # Check if attendance already exists (for 24-hour lock)
        existing_attendance = Attendance.objects.filter(
            subject_id=subject_id,
            class_code=selected_class,
            date=selected_date
        ).first()

        if existing_attendance and not existing_attendance.can_edit():
            can_edit = False

    # SUBMIT / UPDATE ATTENDANCE (POST request)
    if request.method == 'POST':
        selected_date = request.POST['date']
        selected_class = request.POST['class_code']
        present_students = request.POST.getlist('present_students')

        all_students = Student.objects.filter(
            subjects__id=subject_id,
            class_code=selected_class
        )

        for student in all_students:
            Attendance.objects.update_or_create(
                student=student,
                subject_id=subject_id,
                class_code=selected_class,
                date=selected_date,
                defaults={
                    'present': str(student.id) in present_students
                }
            )

        return redirect('teacher_dashboard')

    return render(request, 'teachers/dashboard.html', {
        'teacher': teacher,
        'students': students,
        'can_edit': can_edit,
        'selected_date': selected_date,
        'selected_class': selected_class,
    })

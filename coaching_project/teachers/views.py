from django.shortcuts import render, redirect
from subjects.models import Subject
from students.models import Student
from attendance.models import Attendance
from django.contrib.auth.decorators import login_required

@login_required
def teacher_dashboard(request):
    teacher = request.user.teacher
    subjects = Subject.objects.filter(id=teacher.subject.id)

    students = None
    selected_date = request.GET.get('date')
    selected_subject = request.GET.get('subject')

    # LOAD STUDENTS
    if selected_date and selected_subject:
        students = Student.objects.filter(subjects__id=selected_subject)

    # SUBMIT ATTENDANCE
    if request.method == 'POST':
        date = request.POST['date']
        subject_id = request.POST['subject']
        present_students = request.POST.getlist('present_students')

        all_students = Student.objects.filter(subjects__id=subject_id)

        for student in all_students:
            Attendance.objects.update_or_create(
                student=student,
                subject_id=subject_id,
                date=date,
                defaults={
                    'present': str(student.id) in present_students
                }
            )

        return redirect('teacher_dashboard')

    return render(request, 'teachers/dashboard.html', {
        'subjects': subjects,
        'students': students,
        'selected_date': selected_date,
        'selected_subject': selected_subject,
    })

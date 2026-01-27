from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .models import User
from teachers.models import Teacher, TeacherClass
from subjects.models import Subject
from students.models import Student


def teacher_register(request):
    subjects = Subject.objects.all()

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        subject_id = request.POST['subject']

        # 🔹 MULTIPLE CLASSES
        class_codes = request.POST.getlist('classes')  # ['11', '12']

        # ✅ Password match check
        if password != confirm_password:
            return render(request, 'accounts/teacher_register.html', {
                'subjects': subjects,
                'error': 'Passwords do not match'
            })

        # ✅ Username exists check
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/teacher_register.html', {
                'subjects': subjects,
                'error': 'Username already exists. Please choose another one.'
            })

        # ✅ At least one class selected
        if not class_codes:
            return render(request, 'accounts/teacher_register.html', {
                'subjects': subjects,
                'error': 'Please select at least one class'
            })

        # ✅ Create user
        user = User.objects.create_user(
            username=username,
            password=password,
            role='teacher'
        )

        # ✅ Create teacher profile (WITHOUT classes first)
        teacher = Teacher.objects.create(
            user=user,
            subject_id=subject_id
        )

        # ✅ Assign multiple classes (ManyToMany)
        for code in class_codes:
            cls, _ = TeacherClass.objects.get_or_create(code=code)
            teacher.classes.add(cls)

        return redirect('login')

    return render(request, 'accounts/teacher_register.html', {
        'subjects': subjects
    })




def student_register(request):
    subjects = Subject.objects.all()

    if request.method == 'POST':
        username = request.POST['username']
        class_code = request.POST['class_code']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        subject_ids = request.POST.getlist('subjects')

        # Password match check
        if password != confirm_password:
            return render(request, 'accounts/student_register.html', {
                'subjects': subjects,
                'error': 'Passwords do not match'
            })

        # Username exists check
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/student_register.html', {
                'subjects': subjects,
                'error': 'Username already exists'
            })

        if not subject_ids:
            return render(request, 'accounts/student_register.html', {
                'subjects': subjects,
                'error': 'Please select at least one subject'
            })

        # Create user
        user = User.objects.create_user(
            username=username,
            password=password,
            role='student'
        )

        # Create student profile
        student = Student.objects.create(
            user=user,
            class_code=class_code
        )

        # Assign subjects
        student.subjects.set(subject_ids)

        return redirect('login')

    return render(request, 'accounts/student_register.html', {
        'subjects': subjects
    })




def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.role == 'teacher':
                return redirect('teacher_dashboard')
            else:
                return redirect('student_dashboard')
    return render(request, 'accounts/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')
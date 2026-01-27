from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import User
from teachers.models import Teacher
from subjects.models import Subject
from django.contrib.auth import logout
from django.shortcuts import redirect
from students.models import Student
from django.contrib.auth import authenticate




from django.shortcuts import render, redirect
from .models import User
from teachers.models import Teacher
from subjects.models import Subject

def teacher_register(request):
    subjects = Subject.objects.all()

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        teaching_class = request.POST['teaching_class']
        subject_id = request.POST['subject']

        # ✅ Password match check
        if password != confirm_password:
            return render(request, 'accounts/teacher_register.html', {
                'subjects': subjects,
                'error': 'Passwords do not match'
            })

        # ✅ Username already exists check
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/teacher_register.html', {
                'subjects': subjects,
                'error': 'Username already exists. Please choose another one.'
            })

        # ✅ Create user
        user = User.objects.create_user(
            username=username,
            password=password,
            role='teacher'
        )

        # ✅ Create teacher profile
        Teacher.objects.create(
            user=user,
            teaching_class=teaching_class,
            subject_id=subject_id
        )

        return redirect('login')

    return render(request, 'accounts/teacher_register.html', {
        'subjects': subjects
    })






def student_register(request):
    subjects = Subject.objects.all()

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        subject_ids = request.POST.getlist('subjects')

        # ✅ Password match check
        if password != confirm_password:
            return render(request, 'accounts/student_register.html', {
                'subjects': subjects,
                'error': 'Passwords do not match'
            })

        # ✅ Username exists check
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/student_register.html', {
                'subjects': subjects,
                'error': 'Username already exists. Please choose another one.'
            })

        # ✅ Create user
        user = User.objects.create_user(
            username=username,
            password=password,
            role='student'
        )

        # ✅ Create student profile
        student = Student.objects.create(user=user)

        # ✅ Assign subjects (ManyToMany)
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
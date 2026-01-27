from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def teacher_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role == 'teacher':
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper


def student_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role == 'student':
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper

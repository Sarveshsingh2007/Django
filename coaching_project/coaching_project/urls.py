"""
URL configuration for coaching_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from accounts.views import *
from teachers.views import *
from students.views import *
from django.shortcuts import redirect

def home(request):
    return redirect('login')


urlpatterns = [
    path('', home, name='home'),
    path("admin/", admin.site.urls),
    path('teacher/register/', teacher_register, name='teacher_register'),
    path('student/register/', student_register, name='student_register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('teacher/dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
]

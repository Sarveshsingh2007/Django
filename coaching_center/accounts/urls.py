from django.urls import path
from . import views

urlpatterns = [
    # Registration and Login
    path('', views.register_choice, name='register_choice'),
    path('register/teacher/', views.teacher_register, name='teacher_register'),
    path('register/student/', views.student_register, name='student_register'),
    path('login-choice/', views.login_choice, name='login_choice'),
    path('login/teacher/', views.teacher_login, name='teacher_login'),
    path('login/student/', views.student_login, name='student_login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Home/Dashboard
    path('home/', views.home, name='home'),
    
    # Attendance URLs
    path('attendance/', views.attendance_view, name='attendance'),
    path('attendance/show-students/', views.show_students, name='show_students'),
    path('attendance/submit/', views.submit_attendance, name='submit_attendance'),
    path('attendance/edit/<int:attendance_id>/', views.edit_attendance, name='edit_attendance'),
    
    # Notes URLs
    path('notes/', views.notes_view, name='notes'),
    path('notes/upload/', views.upload_notes, name='upload_notes'),
    path('notes/delete/<int:note_id>/', views.delete_note, name='delete_note'),
    path('notes/download/<int:note_id>/', views.download_note, name='download_note'),
    
    # Fee URLs (Student only)
    path('fees/', views.fees_view, name='fees'),
    
    # Timetable URLs
    path('timetable/', views.timetable_view, name='timetable'),
]
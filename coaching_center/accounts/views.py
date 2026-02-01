from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import (
    TeacherRegistrationForm, 
    StudentRegistrationForm, 
    CaptchaLoginForm,
    AttendanceForm,
    NotesUploadForm
)
from .models import Teacher, Student, Attendance, Notes, Fee, TimeTable, Subject
import random
import json
import string
from django.db.models import Count, Q
from .models import Message, MessageReply
from .forms import MessageForm, MessageReplyForm


# Helper function to generate CAPTCHA
def generate_captcha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


# Registration Choice Page
def register_choice(request):
    return render(request, 'accounts/register_choice.html')


# Teacher Registration
def teacher_register(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Teacher registration successful! You can now login.')
            return redirect('login_choice')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'accounts/teacher_register.html', {'form': form})


# Student Registration
def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Student registration successful! You can now login.')
            return redirect('login_choice')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentRegistrationForm()
    return render(request, 'accounts/student_register.html', {'form': form})


# Login Choice Page
def login_choice(request):
    return render(request, 'accounts/login_choice.html')


# Teacher Login
def teacher_login(request):
    captcha_text = request.session.get('captcha', generate_captcha())
    request.session['captcha'] = captcha_text
    
    if request.method == 'POST':
        form = CaptchaLoginForm(request.POST, captcha_text=captcha_text)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None and user.user_type == 'teacher':
                login(request, user)
                messages.success(request, f'Welcome back, {user.teacher_profile.name}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials or not a teacher account.')
                request.session['captcha'] = generate_captcha()
        else:
            request.session['captcha'] = generate_captcha()
    else:
        form = CaptchaLoginForm(captcha_text=captcha_text)
    
    return render(request, 'accounts/teacher_login.html', {
        'form': form,
        'captcha_text': captcha_text
    })


# Student Login
def student_login(request):
    captcha_text = request.session.get('captcha', generate_captcha())
    request.session['captcha'] = captcha_text
    
    if request.method == 'POST':
        form = CaptchaLoginForm(request.POST, captcha_text=captcha_text)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None and user.user_type == 'student':
                login(request, user)
                messages.success(request, f'Welcome back, {user.student_profile.name}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials or not a student account.')
                request.session['captcha'] = generate_captcha()
        else:
            request.session['captcha'] = generate_captcha()
    else:
        form = CaptchaLoginForm(captcha_text=captcha_text)
    
    return render(request, 'accounts/student_login.html', {
        'form': form,
        'captcha_text': captcha_text
    })


# Logout
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('register_choice')


# Home/Dashboard
@login_required
def home(request):
    user = request.user
    context = {}
    
    if user.user_type == 'teacher':
        teacher = user.teacher_profile
        context = {
            'user_type': 'teacher',
            'profile': teacher,
            'subjects': teacher.subjects.all(),
            'classes': teacher.classes.split(',')
        }
    elif user.user_type == 'student':
        student = user.student_profile
        # Calculate total attendance percentage
        total_classes = Attendance.objects.filter(student=student).count()
        present_classes = Attendance.objects.filter(student=student, is_present=True).count()
        attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        
        context = {
            'user_type': 'student',
            'profile': student,
            'subjects': student.subjects.all(),
            'attendance_percentage': round(attendance_percentage, 2)
        }
    
    return render(request, 'accounts/home.html', context)


# Attendance View
@login_required
def attendance_view(request):
    user = request.user
    
    if user.user_type == 'teacher':
        teacher = user.teacher_profile
        form = AttendanceForm(teacher=teacher)
        return render(request, 'accounts/teacher_attendance.html', {'form': form})
    
    elif user.user_type == 'student':
        student = user.student_profile
        # Get attendance by subject
        subjects = student.subjects.all()
        attendance_data = []
        
        for subject in subjects:
            attendances = Attendance.objects.filter(student=student, subject=subject)
            total = attendances.count()
            present = attendances.filter(is_present=True).count()
            percentage = (present / total * 100) if total > 0 else 0
            
            attendance_data.append({
                'subject': subject,
                'teacher': attendances.first().teacher if attendances.exists() else None,
                'total': total,
                'present': present,
                'percentage': round(percentage, 2),
                'details': attendances.order_by('-date')
            })
        
        # Calculate overall attendance
        total_classes = Attendance.objects.filter(student=student).count()
        present_classes = Attendance.objects.filter(student=student, is_present=True).count()
        overall_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        
        return render(request, 'accounts/student_attendance.html', {
            'attendance_data': attendance_data,
            'overall_percentage': round(overall_percentage, 2),
            'total_classes': total_classes,
            'present_classes': present_classes
        })


# Show Students for Attendance (Teacher)
@login_required
def show_students(request):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        teacher = request.user.teacher_profile
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        class_name = request.POST.get('class_name')
        subject_id = request.POST.get('subject')
        
        subject = get_object_or_404(Subject, id=subject_id)
        
        # Check if teacher has a class at this time
        timetable_entry = TimeTable.objects.filter(
            teacher=teacher,
            day=datetime.strptime(date, '%Y-%m-%d').strftime('%A'),
            time_slot=time_slot,
            class_name=class_name,
            subject=subject
        ).first()
        
        if not timetable_entry:
            messages.error(request, f'You do not have a class scheduled for {time_slot} on this day. Please check your timetable.')
            return redirect('attendance')
        
        # Store in session for submit
        request.session['attendance_date'] = date
        request.session['attendance_time_slot'] = time_slot
        request.session['attendance_class'] = class_name
        request.session['attendance_subject'] = subject_id
        
        students = Student.objects.filter(class_name=class_name, subjects=subject)
        
        # Get existing attendance for this date and time
        existing_attendance = {}
        for student in students:
            att = Attendance.objects.filter(
                student=student,
                subject=subject,
                date=date
            ).first()
            if att:
                existing_attendance[student.id] = {
                    'is_present': att.is_present,
                    'id': att.id,
                    'can_edit': (timezone.now() - att.marked_at).total_seconds() < 86400  # 24 hours
                }
        
        return render(request, 'accounts/show_students.html', {
            'students': students,
            'date': date,
            'time_slot': time_slot,
            'class_name': class_name,
            'subject': subject,
            'existing_attendance': existing_attendance
        })
    
    return redirect('attendance')

# Submit Attendance (Teacher)
@login_required
def submit_attendance(request):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        teacher = request.user.teacher_profile
        date = request.session.get('attendance_date')
        time_slot = request.session.get('attendance_time_slot')
        class_name = request.session.get('attendance_class')
        subject_id = request.session.get('attendance_subject')
        
        subject = get_object_or_404(Subject, id=subject_id)
        students = Student.objects.filter(class_name=class_name, subjects=subject)
        
        for student in students:
            is_present = request.POST.get(f'attendance_{student.id}') == 'on'
            
            # Check if attendance already exists
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                subject=subject,
                date=date,
                defaults={'teacher': teacher, 'is_present': is_present}
            )
            
            if not created:
                # Update if within 24 hours
                if (timezone.now() - attendance.marked_at).total_seconds() < 86400:
                    attendance.is_present = is_present
                    attendance.save()
        
        messages.success(request, f'Attendance marked successfully for {time_slot}!')
        return redirect('attendance')
    
    return redirect('attendance')

# Edit Attendance (Teacher)
@login_required
def edit_attendance(request, attendance_id):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    attendance = get_object_or_404(Attendance, id=attendance_id)
    
    # Check if within 24 hours
    if (timezone.now() - attendance.marked_at).total_seconds() > 86400:
        messages.error(request, 'Cannot edit attendance after 24 hours.')
        return redirect('attendance')
    
    if request.method == 'POST':
        attendance.is_present = not attendance.is_present
        attendance.save()
        messages.success(request, 'Attendance updated successfully!')
    
    return redirect('attendance')


# Notes View
@login_required
def notes_view(request):
    user = request.user
    
    if user.user_type == 'teacher':
        teacher = user.teacher_profile
        notes = Notes.objects.filter(teacher=teacher).select_related('subject')
        form = NotesUploadForm(teacher=teacher)
        
        return render(request, 'accounts/teacher_notes.html', {
            'notes': notes,
            'form': form
        })
    
    elif user.user_type == 'student':
        student = user.student_profile
        # Filter notes by student's class and subjects
        notes = Notes.objects.filter(
            subject__in=student.subjects.all(),
            class_name=student.class_name
        ).select_related('subject', 'teacher')
        
        return render(request, 'accounts/student_notes.html', {
            'notes': notes
        })
    

# Upload Notes (Teacher)
@login_required
def upload_notes(request):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        teacher = request.user.teacher_profile
        form = NotesUploadForm(teacher=teacher, data=request.POST, files=request.FILES)
        
        if form.is_valid():
            note = form.save(commit=False)
            note.teacher = teacher
            note.save()
            messages.success(request, 'Notes uploaded successfully!')
        else:
            messages.error(request, 'Please correct the errors.')
    
    return redirect('notes')


# Delete Notes (Teacher)
@login_required
def delete_note(request, note_id):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    note = get_object_or_404(Notes, id=note_id, teacher=request.user.teacher_profile)
    note.delete()
    messages.success(request, 'Note deleted successfully!')
    
    return redirect('notes')


# Download Notes
@login_required
def download_note(request, note_id):
    note = get_object_or_404(Notes, id=note_id)
    
    # Check if user has access
    if request.user.user_type == 'student':
        student = request.user.student_profile
        if note.subject not in student.subjects.all():
            messages.error(request, 'Access denied.')
            return redirect('notes')
    elif request.user.user_type == 'teacher':
        teacher = request.user.teacher_profile
        if note.teacher != teacher:
            messages.error(request, 'Access denied.')
            return redirect('notes')
    
    response = FileResponse(note.file.open(), as_attachment=True, filename=note.file.name)
    return response


# Fees View (Student only)
@login_required
def fees_view(request):
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    student = request.user.student_profile
    fees = Fee.objects.filter(student=student).order_by('-year', '-id')
    
    return render(request, 'accounts/student_fees.html', {
        'fees': fees
    })


# Timetable View
@login_required
def timetable_view(request):
    user = request.user
    
    if user.user_type == 'teacher':
        teacher = user.teacher_profile
        timetable = TimeTable.objects.filter(teacher=teacher).select_related('subject')
        
        # Organize by day and time
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        times = ['3:30-4:30 PM', '4:30-5:30 PM']
        
        schedule = {}
        for day in days:
            schedule[day] = {}
            for time in times:
                entry = timetable.filter(day=day, time_slot=time).first()
                schedule[day][time] = entry
        
        return render(request, 'accounts/teacher_timetable.html', {
            'schedule': schedule,
            'days': days,
            'times': times
        })
    
    elif user.user_type == 'student':
        student = user.student_profile
        timetable = TimeTable.objects.filter(class_name=student.class_name).select_related('subject', 'teacher')
        
        # Organize by day and time
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        times = ['3:30-4:30 PM', '4:30-5:30 PM']
        
        schedule = {}
        for day in days:
            schedule[day] = {}
            for time in times:
                entry = timetable.filter(day=day, time_slot=time).first()
                schedule[day][time] = entry
        
        return render(request, 'accounts/student_timetable.html', {
            'schedule': schedule,
            'days': days,
            'times': times
        })
    

# Student: Send Message to Teacher
@login_required
def send_message(request):
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can send messages.')
        return redirect('home')
    
    student = request.user.student_profile
    
    if request.method == 'POST':
        form = MessageForm(student=student, data=request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.student = student
            message.save()
            messages.success(request, f'Message sent successfully to {message.teacher.name}!')
            return redirect('inbox')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MessageForm(student=student)
    
    # Create teacher-subjects mapping for JavaScript
    student_subjects = student.subjects.all()
    teacher_ids = TimeTable.objects.filter(
        class_name=student.class_name,
        subject__in=student_subjects
    ).values_list('teacher_id', flat=True).distinct()
    
    teachers = Teacher.objects.filter(id__in=teacher_ids)
    
    # Build dictionary: teacher_id -> list of subjects they teach (that student is enrolled in)
    teacher_subjects_map = {}
    for teacher in teachers:
        # Get subjects this teacher teaches that the student is also enrolled in
        common_subjects = teacher.subjects.filter(id__in=student_subjects.values_list('id', flat=True))
        teacher_subjects_map[teacher.id] = [
            {'id': subject.id, 'name': subject.name}
            for subject in common_subjects
        ]
    
    
    teacher_subjects_json = json.dumps(teacher_subjects_map)
    
    return render(request, 'accounts/send_message.html', {
        'form': form,
        'teacher_subjects_json': teacher_subjects_json
    })

# Student: View Sent Messages and Replies (Inbox)
@login_required
def inbox(request):
    user = request.user
    
    if user.user_type == 'student':
        student = user.student_profile
        sent_messages = Message.objects.filter(student=student).select_related('teacher', 'subject')
        
        return render(request, 'accounts/student_inbox.html', {
            'messages': sent_messages
        })
    
    elif user.user_type == 'teacher':
        teacher = user.teacher_profile
        received_messages = Message.objects.filter(teacher=teacher).select_related('student', 'subject')
        
        # Count unread messages
        unread_count = received_messages.filter(status='unread').count()
        
        return render(request, 'accounts/teacher_inbox.html', {
            'messages': received_messages,
            'unread_count': unread_count
        })


# View Message Thread (Both Student and Teacher)
@login_required
def view_message(request, message_id):
    message_obj = get_object_or_404(Message, id=message_id)
    user = request.user
    
    # Check access permissions
    if user.user_type == 'student':
        if message_obj.student != user.student_profile:
            messages.error(request, 'You do not have permission to view this message.')
            return redirect('inbox')
    elif user.user_type == 'teacher':
        if message_obj.teacher != user.teacher_profile:
            messages.error(request, 'You do not have permission to view this message.')
            return redirect('inbox')
        # Mark as read when teacher views
        if message_obj.status == 'unread':
            message_obj.status = 'read'
            message_obj.save()
    
    # Get all replies
    replies = message_obj.replies.all()
    
    # Handle reply submission
    if request.method == 'POST':
        form = MessageReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.message = message_obj
            reply.sender_type = user.user_type
            reply.save()
            
            # Update message status
            if user.user_type == 'teacher':
                message_obj.status = 'replied'
                message_obj.save()
            
            messages.success(request, 'Reply sent successfully!')
            return redirect('view_message', message_id=message_id)
    else:
        form = MessageReplyForm()
    
    return render(request, 'accounts/view_message.html', {
        'message': message_obj,
        'replies': replies,
        'form': form
    })


# Teacher: Delete Message
@login_required
def delete_message(request, message_id):
    if request.user.user_type != 'teacher':
        messages.error(request, 'Only teachers can delete messages.')
        return redirect('home')
    
    message_obj = get_object_or_404(Message, id=message_id, teacher=request.user.teacher_profile)
    message_obj.delete()
    messages.success(request, 'Message deleted successfully!')
    
    return redirect('inbox')    
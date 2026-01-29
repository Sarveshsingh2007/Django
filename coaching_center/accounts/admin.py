from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Teacher, Student, Subject, Attendance, Notes, Fee, TimeTable

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'user_type', 'is_staff']
    list_filter = ['user_type', 'is_staff', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['teacher_id', 'name', 'mobile', 'classes', 'created_at']
    search_fields = ['name', 'teacher_id', 'mobile']
    list_filter = ['classes', 'created_at']
    filter_horizontal = ['subjects']
    readonly_fields = ['teacher_id', 'created_at']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'name', 'class_name', 'mobile', 'created_at']
    search_fields = ['name', 'student_id', 'mobile']
    list_filter = ['class_name', 'created_at']
    filter_horizontal = ['subjects']
    readonly_fields = ['student_id', 'created_at']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'date', 'is_present', 'teacher', 'marked_at']
    list_filter = ['date', 'is_present', 'subject']
    search_fields = ['student__name', 'student__student_id']
    date_hierarchy = 'date'
    readonly_fields = ['marked_at', 'updated_at']


@admin.register(Notes)
class NotesAdmin(admin.ModelAdmin):
    list_display = ['subject', 'topic', 'teacher', 'uploaded_at']
    list_filter = ['subject', 'uploaded_at']
    search_fields = ['topic', 'subject__name']
    date_hierarchy = 'uploaded_at'
    readonly_fields = ['uploaded_at']


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ['student', 'month', 'year', 'amount', 'status', 'paid_date']
    list_filter = ['status', 'month', 'year']
    search_fields = ['student__name', 'student__student_id']
    list_editable = ['status']


@admin.register(TimeTable)
class TimeTableAdmin(admin.ModelAdmin):
    list_display = ['day', 'time_slot', 'class_name', 'subject', 'teacher']
    list_filter = ['day', 'class_name', 'time_slot']
    search_fields = ['subject__name', 'teacher__name']
from django.contrib import admin
from .models import*

# Register your models here.


admin.site.register(Recipe)

admin.site.register(StudentID)
admin.site.register(Student)
admin.site.register(Department)


class SubjectMarkAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'marks']

admin.site.register(Subject)
admin.site.register(SubjectMarks, SubjectMarkAdmin)
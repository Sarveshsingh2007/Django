from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Teacher, Student, Subject, Attendance, Notes
from django.core.exceptions import ValidationError
import random
import string

class TeacherRegistrationForm(UserCreationForm):
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    mobile = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit Mobile Number'})
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    CLASSES_CHOICES = [
        ('11', 'Class 11th'),
        ('12', 'Class 12th'),
    ]
    
    classes = forms.MultipleChoiceField(
        choices=CLASSES_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True
    )
    
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Re-enter Password'})
    
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if not mobile.isdigit() or len(mobile) != 10:
            raise ValidationError('Mobile number must be exactly 10 digits.')
        return mobile
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'teacher'
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create Teacher profile
            teacher = Teacher.objects.create(
                user=user,
                name=self.cleaned_data['name'],
                mobile=self.cleaned_data['mobile'],
                classes=','.join(self.cleaned_data['classes']),
                image=self.cleaned_data.get('image')
            )
            teacher.subjects.set(self.cleaned_data['subjects'])
        return user


class StudentRegistrationForm(UserCreationForm):
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    mobile = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit Mobile Number'})
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    CLASS_CHOICES = [
        ('11', 'Class 11th'),
        ('12', 'Class 12th'),
    ]
    
    class_name = forms.ChoiceField(
        choices=CLASS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Re-enter Password'})
    
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if not mobile.isdigit() or len(mobile) != 10:
            raise ValidationError('Mobile number must be exactly 10 digits.')
        return mobile
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create Student profile
            student = Student.objects.create(
                user=user,
                name=self.cleaned_data['name'],
                mobile=self.cleaned_data['mobile'],
                class_name=self.cleaned_data['class_name'],
                image=self.cleaned_data.get('image')
            )
            student.subjects.set(self.cleaned_data['subjects'])
        return user


class CaptchaLoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    captcha = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter CAPTCHA'})
    )
    
    def __init__(self, *args, **kwargs):
        self.captcha_text = kwargs.pop('captcha_text', None)
        super().__init__(*args, **kwargs)
    
    def clean_captcha(self):
        captcha = self.cleaned_data.get('captcha')
        if captcha != self.captcha_text:
            raise ValidationError('Invalid CAPTCHA. Please try again.')
        return captcha


class AttendanceForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    class_name = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    def __init__(self, teacher=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher:
            # Get teacher's classes
            classes = teacher.classes.split(',')
            self.fields['class_name'].choices = [(c, f'Class {c}th') for c in classes]
            # Get teacher's subjects
            self.fields['subject'].queryset = teacher.subjects.all()


class NotesUploadForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ['subject', 'topic', 'file']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'topic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Topic Name'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, teacher=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['subject'].queryset = teacher.subjects.all()
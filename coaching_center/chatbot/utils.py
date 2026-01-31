from accounts.models import Teacher, Student, Subject, TimeTable, Fee, Notes
from django.contrib.auth import get_user_model
from .models import FAQ
import json

User = get_user_model()

def get_coaching_context(user=None):
    """Generate context about the coaching center for the AI"""
    
    context = {
        "coaching_name": "Excellence Coaching Center",
        "classes_offered": ["Class 11th", "Class 12th"],
        "subjects": list(Subject.objects.values_list('name', flat=True)),
        "timings": "Classes are conducted from Monday to Friday, 3:30 PM to 5:30 PM",
        "total_teachers": Teacher.objects.count(),
        "total_students": Student.objects.count(),
    }
    
    # Add user-specific context
    if user and user.is_authenticated:
        if user.user_type == 'student':
            try:
                student = user.student_profile
                context['user_info'] = {
                    'name': student.name,
                    'student_id': student.student_id,
                    'class': f"Class {student.class_name}th",
                    'subjects': list(student.subjects.values_list('name', flat=True)),
                }
                
                # Get user's timetable
                timetable = TimeTable.objects.filter(class_name=student.class_name)
                context['user_timetable'] = [
                    {
                        'day': tt.day,
                        'time': tt.time_slot,
                        'subject': tt.subject.name,
                        'teacher': tt.teacher.name
                    }
                    for tt in timetable
                ]
                
                # Get fee status
                fees = Fee.objects.filter(student=student).order_by('-year', '-id')[:3]
                context['fee_info'] = [
                    {
                        'month': fee.month,
                        'year': fee.year,
                        'amount': str(fee.amount),
                        'status': fee.status
                    }
                    for fee in fees
                ]
                
            except Student.DoesNotExist:
                pass
                
        elif user.user_type == 'teacher':
            try:
                teacher = user.teacher_profile
                context['user_info'] = {
                    'name': teacher.name,
                    'teacher_id': teacher.teacher_id,
                    'subjects': list(teacher.subjects.values_list('name', flat=True)),
                    'classes': teacher.classes.split(',')
                }
                
                # Get teacher's timetable
                timetable = TimeTable.objects.filter(teacher=teacher)
                context['user_timetable'] = [
                    {
                        'day': tt.day,
                        'time': tt.time_slot,
                        'subject': tt.subject.name,
                        'class': f"Class {tt.class_name}th"
                    }
                    for tt in timetable
                ]
                
            except Teacher.DoesNotExist:
                pass
    
    return context


def get_faq_context():
    """Get all FAQs for the AI"""
    faqs = FAQ.objects.filter(is_active=True)
    faq_list = [
        {
            'category': faq.category,
            'question': faq.question,
            'answer': faq.answer
        }
        for faq in faqs
    ]
    return faq_list


def build_system_prompt(user=None):
    """Build the system prompt for Claude"""
    
    context = get_coaching_context(user)
    faqs = get_faq_context()
    
    system_prompt = f"""You are an AI assistant for {context['coaching_name']}, a coaching center that offers education for {', '.join(context['classes_offered'])}.

**Your Role:**
- Help students, teachers, and visitors with their queries
- Provide accurate information about the coaching center
- Be friendly, professional, and concise
- Guide users to the right sections of the website when needed

**Coaching Center Information:**
- Classes Offered: {', '.join(context['classes_offered'])}
- Subjects: {', '.join(context['subjects'])}
- Class Timings: {context['timings']}
- Total Teachers: {context['total_teachers']}
- Total Students: {context['total_students']}

**Available FAQs:**
{json.dumps(faqs, indent=2)}
"""

    if user and user.is_authenticated and 'user_info' in context:
        system_prompt += f"""

**Current User Information:**
{json.dumps(context['user_info'], indent=2)}
"""
        
        if 'user_timetable' in context:
            system_prompt += f"""

**User's Timetable:**
{json.dumps(context['user_timetable'], indent=2)}
"""
        
        if 'fee_info' in context:
            system_prompt += f"""

**Recent Fee Information:**
{json.dumps(context['fee_info'], indent=2)}
"""

    system_prompt += """

**Important Guidelines:**
1. Always be polite and helpful
2. If you don't know something, admit it and suggest contacting the administration
3. For personal information (like specific grades or detailed attendance), guide users to check their dashboard
4. Keep responses concise and clear
5. Use bullet points for lists
6. If asked about functionality, guide them to the appropriate section (e.g., "You can view your timetable by clicking on 'Time Table' in the navigation menu")
7. Never make up information - only use the data provided above
8. For sensitive information (passwords, personal details), remind users never to share such information

**Response Format:**
- Keep responses under 200 words when possible
- Use emojis sparingly (only when appropriate)
- Structure longer responses with bullet points
- End with a question if clarification is needed
"""

    return system_prompt
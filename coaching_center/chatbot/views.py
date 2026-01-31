from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import ChatSession, ChatMessage, FAQ
from .utils import build_system_prompt
import json
import uuid

# chatbot with better keyword matching
def get_bot_response_simple(message, user=None):
    """Improved rule-based responses with better keyword matching"""
    
    message_lower = message.lower()
    
    # Greeting
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return "Hello! 👋 Welcome to Excellence Coaching Center. How can I help you today?\n\nYou can ask me about:\n• Registration and admission\n• Fee details\n• Class timings\n• Subjects and teachers\n• Attendance and notes"
    
    # Mark Attendance (Teacher specific)
    if ('mark' in message_lower or 'take' in message_lower or 'submit' in message_lower) and 'attendance' in message_lower:
        if user and user.is_authenticated and user.user_type == 'teacher':
            return "📋 To mark attendance:\n\n1. Click on 'Attendance' in the navigation menu\n2. Select the date\n3. Select the time slot (3:30-4:30 PM or 4:30-5:30 PM)\n4. Choose your class\n5. Select the subject\n6. Click 'Show Students'\n7. Mark students as present/absent\n8. Click 'Submit'\n\n⚠️ Note: You can edit attendance within 24 hours of marking."
        elif user and user.is_authenticated and user.user_type == 'student':
            return "📊 As a student, you cannot mark attendance. Only teachers can mark attendance.\n\nYou can view your attendance by clicking on 'Attendance' in the menu."
        else:
            return "📋 Attendance marking is for teachers only.\n\nTeachers can:\n• Mark daily attendance\n• Select date, time, class, and subject\n• Edit attendance within 24 hours\n\nPlease login as a teacher to mark attendance."
    
    # View/Check Attendance
    if ('view' in message_lower or 'check' in message_lower or 'see' in message_lower or 'show' in message_lower) and 'attendance' in message_lower:
        if user and user.is_authenticated and user.user_type == 'student':
            return "📊 To view your attendance:\n\n1. Click on 'Attendance' in the navigation menu\n2. You'll see your overall attendance percentage\n3. View subject-wise attendance details\n4. Click 'Show Details' to see date-wise records\n\n💡 Tip: Maintain at least 75% attendance for best results!"
        elif user and user.is_authenticated and user.user_type == 'teacher':
            return "📊 As a teacher, you can view attendance records in the Attendance section after marking them.\n\nYou can also mark new attendance or edit existing ones (within 24 hours)."
        else:
            return "📊 Please login to view attendance records.\n\nStudents can see their attendance percentage and detailed records."
    
    # General Attendance (when just "attendance" is mentioned)
    if 'attendance' in message_lower or 'absent' in message_lower or 'present' in message_lower:
        if user and user.is_authenticated:
            if user.user_type == 'student':
                return "📊 View your attendance:\n\n1. Click on 'Attendance' in the menu\n2. See your overall attendance percentage\n3. View subject-wise attendance\n4. Check detailed attendance records\n\nMaintain at least 75% attendance for best results!"
            else:
                return "📋 Mark attendance:\n\n1. Go to 'Attendance' section\n2. Select date, time, class, and subject\n3. Click 'Show Students'\n4. Mark present/absent\n5. Submit\n\nYou can edit attendance within 24 hours of marking."
        return "📊 Attendance tracking:\n• Teachers mark attendance daily\n• Students can view their attendance records\n• Detailed subject-wise attendance available\n• Login to check your attendance!"
    
    # Registration
    if 'register' in message_lower or 'admission' in message_lower or 'enroll' in message_lower or 'sign up' in message_lower or 'join' in message_lower:
        return "📝 To register:\n\n1. Click on 'Register' at the top\n2. Choose 'Student' or 'Teacher'\n3. Fill in your details:\n   • Profile picture\n   • Full name and username\n   • Email and mobile number\n   • Class and subjects\n   • Create a password\n4. Click 'Submit'\n\nAfter registration, you can login with your username and password!"
    
    # Login
    if 'login' in message_lower or 'log in' in message_lower or 'sign in' in message_lower:
        return "🔐 To login:\n\n1. Click on 'Login' in the menu\n2. Choose 'Student Login' or 'Teacher Login'\n3. Enter your username and password\n4. Enter the CAPTCHA code\n5. Click 'Login'\n\nForgot your credentials? Contact the administration office."
    
    # Upload Notes (Teacher)
    if ('upload' in message_lower or 'add' in message_lower or 'post' in message_lower) and 'note' in message_lower:
        if user and user.is_authenticated and user.user_type == 'teacher':
            return "📤 To upload notes:\n\n1. Go to 'Notes' section\n2. Select subject from your teaching subjects\n3. Select the class (11th or 12th)\n4. Enter topic name\n5. Choose file (PDF, DOC, PPT, etc.)\n6. Click 'Upload Notes'\n\nStudents in that class and subject will be able to download your notes!"
        elif user and user.is_authenticated and user.user_type == 'student':
            return "📚 As a student, you cannot upload notes. Only teachers can upload notes.\n\nYou can download notes uploaded by your teachers from the 'Notes' section."
        else:
            return "📤 Note uploading is for teachers only.\n\nTeachers can upload:\n• PDF documents\n• Word files\n• PowerPoint presentations\n• Study materials\n\nLogin as a teacher to upload notes."
    
    # Download/View Notes
    if ('download' in message_lower or 'view' in message_lower or 'get' in message_lower or 'see' in message_lower) and 'note' in message_lower:
        if user and user.is_authenticated and user.user_type == 'student':
            return "📚 To download notes:\n\n1. Click on 'Notes' in the menu\n2. Browse notes by subject\n3. You'll see notes uploaded by your teachers\n4. Click 'Download' button to save the file\n\nNotes are available only for your registered class and subjects!"
        elif user and user.is_authenticated and user.user_type == 'teacher':
            return "📚 You can view and manage your uploaded notes in the 'Notes' section.\n\nYou can:\n• Upload new notes\n• Download your notes\n• Delete notes you uploaded"
        else:
            return "📚 Login to access study notes!\n\nStudents can:\n• View notes by subject\n• Download PDF/documents\n• Access materials uploaded by teachers"
    
    # General Notes
    if 'note' in message_lower or 'study material' in message_lower:
        if user and user.is_authenticated:
            if user.user_type == 'student':
                return "📚 Access study notes:\n\n1. Click on 'Notes' in the menu\n2. Browse notes by subject and class\n3. Download PDF/documents\n4. Study materials uploaded by your teachers\n\nNew notes are added regularly!"
            else:
                return "📤 Upload notes:\n\n1. Go to 'Notes' section\n2. Select subject and class\n3. Enter topic name\n4. Upload file\n5. Click 'Upload'\n\nStudents will be able to download your notes!"
        return "📚 Study Notes:\n• Teachers upload notes regularly\n• Available by subject and topic\n• Download anytime after login\n• Access from 'Notes' section\n\nLogin to access study materials!"
    
    # Fees - Check/View
    if ('check' in message_lower or 'view' in message_lower or 'see' in message_lower or 'show' in message_lower) and ('fee' in message_lower or 'payment' in message_lower):
        if user and user.is_authenticated and user.user_type == 'student':
            return "💰 To view your fees:\n\n1. Click on 'Fees' in the navigation menu\n2. You'll see:\n   • Monthly fee amounts\n   • Payment status (Paid/Pending/Overdue)\n   • Payment dates\n\nFor payment queries, contact the administration office."
        else:
            return "💰 Login as a student to view your fee details.\n\nThe fee section shows:\n• Monthly fees\n• Payment status\n• Payment history"
    
    # Fees - Pay/Payment
    if ('pay' in message_lower or 'payment' in message_lower) and 'fee' in message_lower:
        return "💳 To pay fees:\n\n• Visit the administration office\n• Payment should be made by 10th of each month\n• Keep your payment receipt safe\n\nYou can check your payment status in the 'Fees' section after logging in."
    
    # General Fees
    if 'fee' in message_lower or 'cost' in message_lower or 'price' in message_lower:
        if user and user.is_authenticated and user.user_type == 'student':
            return "💰 View your fee details by clicking on 'Fees' in the navigation menu.\n\nYou'll see:\n• Monthly fee amounts\n• Payment status\n• Payment dates\n\nFor payment queries, contact administration."
        return "💰 Fee information:\n• Monthly fees vary by class and subjects\n• Payment by 10th of each month\n• Students can view details in 'Fees' section\n\nLogin to see your specific fee structure."
    
    # Timetable - View
    if 'timetable' in message_lower or 'schedule' in message_lower or 'timing' in message_lower or 'time table' in message_lower or 'class time' in message_lower:
        if user and user.is_authenticated:
            return "📅 To view your timetable:\n\n1. Click on 'Time Table' in the menu\n2. You'll see your complete weekly schedule\n\nSchedule:\n• Days: Monday to Friday\n• Timings: 3:30-4:30 PM and 4:30-5:30 PM\n• Each class is 1 hour long"
        return "📅 Class Schedule:\n• Days: Monday to Friday\n• Timing: 3:30 PM - 5:30 PM\n• Two sessions daily:\n  - 3:30-4:30 PM\n  - 4:30-5:30 PM\n\nLogin to see your personalized timetable!"
    
    # Teachers
    if 'teacher' in message_lower or 'faculty' in message_lower or 'staff' in message_lower or 'instructor' in message_lower:
        return "👨‍🏫 Our Faculty:\n\nWe have experienced teachers for:\n• Physics\n• Chemistry\n• Mathematics\n• Biology\n• English\n\nAll teachers are qualified and experienced. You can view teacher details in your timetable after logging in!"
    
    # Subjects
    if 'subject' in message_lower or 'course' in message_lower:
        return "📖 Subjects Offered:\n\n✓ Physics\n✓ Chemistry\n✓ Mathematics\n✓ Biology\n✓ English\n\nAvailable for Class 11th and 12th. Students can choose subjects based on their stream (PCM/PCB)."
    
    # Classes
    if 'class' in message_lower and ('which' in message_lower or 'what' in message_lower or 'offered' in message_lower):
        return "🏫 Classes Offered:\n\n• Class 11th\n• Class 12th\n\nWe provide coaching for both science and commerce streams with experienced faculty."
    
    # Help
    if 'help' in message_lower or 'support' in message_lower:
        return "🆘 I can help you with:\n\n✓ Registration and login\n✓ Fee information\n✓ Class timings and timetable\n✓ Attendance (marking/viewing)\n✓ Study notes (upload/download)\n✓ Teacher information\n✓ General queries\n\nJust ask me anything!"
    
    # Contact
    if 'contact' in message_lower or 'phone' in message_lower or 'email' in message_lower or 'address' in message_lower or 'reach' in message_lower:
        return "📞 Contact Information:\n\nFor detailed queries:\n• Visit the administration office during working hours\n• Office Hours: 9:00 AM - 6:00 PM (Mon-Sat)\n• Or ask your specific question here!\n\nI'm here to help! 😊"
    
    # Thank you
    if 'thank' in message_lower or 'thanks' in message_lower:
        return "You're welcome! 😊 Is there anything else I can help you with?"
    
    # Bye
    if 'bye' in message_lower or 'goodbye' in message_lower or 'see you' in message_lower:
        return "Goodbye! 👋 Feel free to come back anytime if you have more questions. Have a great day!"
    
    # Password/Account issues
    if 'password' in message_lower or 'forgot' in message_lower or 'reset' in message_lower:
        return "🔐 For password issues:\n\n• Contact the administration office\n• They can help you reset your password\n• Never share your password with anyone\n\nFor security reasons, password reset must be done through admin."
    
    # Hours/Timing (general)
    if ('hour' in message_lower or 'open' in message_lower or 'close' in message_lower) and 'office' not in message_lower:
        return "🕐 Coaching Center Hours:\n\nClasses:\n• Monday to Friday\n• 3:30 PM - 5:30 PM\n\nOffice Hours:\n• Monday to Saturday\n• 9:00 AM - 6:00 PM"
    
    # Profile/Account
    if 'profile' in message_lower or 'account' in message_lower or 'details' in message_lower:
        if user and user.is_authenticated:
            return "👤 Your profile information is available on the Home page.\n\nClick on 'Home' in the menu to see:\n• Your ID\n• Contact details\n• Class and subjects\n• Other information"
        return "👤 Login to access your profile and account details."
    
    # Default response - when no keywords match
    return "I didn't quite understand that. 🤔\n\nI can help you with:\n\n📝 Registration & Login\n💰 Fees & Payments\n📅 Timetable & Schedule\n📊 Attendance (mark/view)\n📚 Study Notes (upload/download)\n👨‍🏫 Teachers & Subjects\n\nCould you rephrase your question or choose a topic from above?"

@csrf_exempt
def chatbot_message(request):
    """Handle chatbot messages"""
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            session_id = data.get('session_id')
            
            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            
            # Get or create session
            if not session_id:
                session_id = str(uuid.uuid4())
                session = ChatSession.objects.create(
                    session_id=session_id,
                    user=request.user if request.user.is_authenticated else None
                )
            else:
                session = ChatSession.objects.get(session_id=session_id)
            
            # Save user message
            ChatMessage.objects.create(
                session=session,
                message=message,
                is_bot=False
            )
            
            # Get bot response (using simple rule-based system)
            bot_response = get_bot_response_simple(message, request.user if request.user.is_authenticated else None)
            
            # Save bot response
            ChatMessage.objects.create(
                session=session,
                message=bot_response,
                is_bot=True
            )
            
            return JsonResponse({
                'response': bot_response,
                'session_id': session_id
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST requests allowed'}, status=405)


def chatbot_history(request, session_id):
    """Get chat history for a session"""
    
    try:
        session = ChatSession.objects.get(session_id=session_id)
        messages = session.messages.all()
        
        message_list = [
            {
                'message': msg.message,
                'is_bot': msg.is_bot,
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            for msg in messages
        ]
        
        return JsonResponse({'messages': message_list})
        
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
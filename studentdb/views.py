from django.shortcuts import render, redirect, get_object_or_404
from .models import Student
from sentimentdb.models import Teacher,Course,Feedback
from django.contrib import messages
from .utils import predict_sentiment

from django.contrib.auth.hashers import make_password,check_password
from django.core.exceptions import ValidationError
# Create your views here.
def log(request):
     if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
             user = Student.objects.get(username=username)
             if check_password(password, user.password):
                # Storing user data in session
                request.session['fname'] = user.fname
                request.session['lname'] = user.lname
                request.session['username'] = user.username
                request.session['email'] = user.email
                return redirect('studentDashboard')  # Assuming 'dashboard' is the name of the url pattern for the dashboard view
             else:
                messages.error(request, 'Invalid username or password')
               
        except Student.DoesNotExist:
            messages.error(request, 'Invalid username or password')
            return redirect('student-login')
        
     return render(request, 'students/page-login.html')

def dashboard_view(request):
    if 'username' not in request.session:
        return redirect('student-login')
    
    return render(request, 'students/index.html')



def predict_feedback_sentiment(request):
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback')
        if feedback_text:
            sentiment, probabilities = predict_sentiment(feedback_text)
            category = "good" if sentiment == 1 else "bad" if sentiment == -1 else "neutral"
            return render(request, 'students/predict_sentiment.html', {
                'sentiment':category ,
                'probabilities': probabilities.tolist(),
                'feedback_text': feedback_text
            })
    return render(request, 'students/predict_sentiment.html')


def list_teachers(request):
    teachers = Teacher.objects.all()
    return render(request, 'students/teacher.html', {'teachers': teachers})

def list_courses(request):
    courses = Course.objects.all()
    return render(request, 'students/course.html', {'courses': courses})

def submit_teacher_feedback(request, teacher_id):
    if request.method == 'POST':
        teacher = get_object_or_404(Teacher, id=teacher_id)
        student_username = request.session.get('username')
        student = Student.objects.get(username=student_username)
        feedback_text = request.POST.get('feedback')
        
        sentiment, probabilities = predict_sentiment(feedback_text)
        category = "positive" if sentiment == 1 else "negative" if sentiment == -1 else "neutral"
        Feedback.objects.create(
            content=feedback_text,
            sentiment=category,
            student=student,
            teacher=teacher
        )
        messages.success(request, 'Feedback submitted successfully!')
    return redirect('list_teachers')

def submit_course_feedback(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        student_username = request.session.get('username')
        student = Student.objects.get(username=student_username)
        feedback_text = request.POST.get('feedback')

        sentiment, probabilities = predict_sentiment(feedback_text)
        category = "positive" if sentiment == 1 else "negative" if sentiment == -1 else "neutral"

        Feedback.objects.create(
            content=feedback_text,
            sentiment=category,
            student=student,
            course=course
        )
        messages.success(request, 'Feedback submitted successfully!')
    return redirect('list_courses')


def profile(request):
    profile = Student.objects.get(username=request.session['username'])

    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        new_username = request.POST.get('new_username')
        new_email = request.POST.get('new_email')

        if new_password and new_password != confirm_password:
            messages.error(request, "New password and confirm password do not match.")
        elif not check_password(old_password, profile.password):
            messages.error(request, "Old password is incorrect.")
        else:
            if new_password:
                profile.password = new_password

            if new_username and new_username != profile.username:
                if Student.objects.filter(username=new_username).exists():
                    messages.error(request, "Username already exists.")
                else:
                    profile.username = new_username

            if new_email and new_email != profile.email:
                if Student.objects.filter(email=new_email).exists():
                    messages.error(request, "Email already exists.")
                else:
                    profile.email = new_email

            profile.save()
            messages.success(request, "Profile successfully updated.")
            return redirect('profileSt')

    return render(request, 'students/profile.html', {'student': profile})


def logout(request):
    request.session.flush()
    return render(request, 'students/page-login.html')
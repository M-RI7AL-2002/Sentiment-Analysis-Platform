from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
# Create your views here.
from .models import Profile,Feedback,Teacher,Course,Todo
from studentdb.models import Student
from django.contrib import messages
from django.db.models import Avg, Q,Count
from .forms import TeacherForm,CourseForm,StudentForm
from datetime import date
from dateutil.relativedelta import relativedelta # type: ignore
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
from django.contrib.auth.hashers import check_password, make_password
from studentdb.models import Student
def log(request):
     if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = Profile.objects.get(username=username)
            if check_password(password, user.password):
                # Storing user data in session
                request.session['fname'] = user.fname
                request.session['lname'] = user.lname
                request.session['username'] = user.username
                request.session['email'] = user.email
                return redirect('dashboard')  # Assuming 'dashboard' is the name of the url pattern for the dashboard view
            else:
                messages.error(request, 'Invalid username or password')
        except Profile.DoesNotExist:
            messages.error(request, 'Invalid username or password')
        
        return redirect('page-login')
        
     return render(request, 'theme/page-login.html')

def dashboard_view(request):
    if 'username' not in request.session:
        messages.error(request, 'you must log in first')
        return redirect('page-login')
    

    total_feedback = Feedback.objects.count()

    teachers = Teacher.objects.all()
    teacher_data = []

    for teacher in teachers:
        positive_feedback_count = Feedback.objects.filter(teacher=teacher, sentiment='positive').count()
        teacher_data.append({
            'fname': teacher.fname,
            'lname': teacher.lname,
            'email': teacher.email,
            'positive_feedbacks': positive_feedback_count,
        })
    courses=Course.objects.all()
    course_data=[]

    for course in courses:
        positive_feedback_count=Feedback.objects.filter(course=course, sentiment='positive').count()
        course_data.append({
            'name':course.name,
            'positive_feedbacks':positive_feedback_count,
        })
 
    # Calculate total feedbacks for teachers and courses
    total_teacher_feedbacks = Feedback.objects.filter(teacher__isnull=False).count()
    total_course_feedbacks = Feedback.objects.filter(course__isnull=False).count()
    
    # Calculate total positive feedbacks for teachers and courses
    total_teacher_positive_feedbacks = Feedback.objects.filter(teacher__isnull=False, sentiment='positive').count()
    total_course_positive_feedbacks = Feedback.objects.filter(course__isnull=False, sentiment='positive').count()
    
    # Calculate percentages
    if total_teacher_feedbacks > 0:
        teacher_positive_percentage = round((total_teacher_positive_feedbacks / total_teacher_feedbacks) * 100,2)
    else:
        teacher_positive_percentage = 0
    
    if total_course_feedbacks > 0:
        course_positive_percentage = round((total_course_positive_feedbacks / total_course_feedbacks) * 100,2)
    else:
        course_positive_percentage = 0

    
    total_feedbacks = Feedback.objects.count()
    total_positive_feedbacks = Feedback.objects.filter(sentiment='positive').count()
    
    if total_feedbacks > 0:
        positive_feedback_percentage = round((total_positive_feedbacks / total_feedbacks) * 100,2)
    else:
        positive_feedback_percentage = 0


    context = {
        'total_feedback': total_feedback,
        'positive_feedback': total_positive_feedbacks,
        'neutral_feedback': Feedback.objects.filter(sentiment='neutral').count(),
        'negative_feedback': Feedback.objects.filter(sentiment='negative').count(),
        'total_teachers':Teacher.objects.count(),
        'total_courses':Course.objects.count(),
        'total_students':Student.objects.count(),
        'teacher_data':teacher_data,
        'course_data':course_data,
        'teacher_positive_percentage': teacher_positive_percentage,
        'course_positive_percentage': course_positive_percentage,
        'positive_feedback_percentage': positive_feedback_percentage,
    }
    
    return render(request, 'theme/index.html',context)



def logout(request):
    request.session.flush()
    return render(request, 'theme/page-login.html')



def teacherAn(request):
    if 'username' not in request.session:
        messages.error(request, 'you must log in first')
        return redirect('page-login')


    total_teachers = Teacher.objects.count()
    total_positive_feedbacks = Feedback.objects.filter(teacher__isnull=False, sentiment='positive').count()
    total_negative_feedbacks = Feedback.objects.filter(teacher__isnull=False, sentiment='negative').count()
    total_neutral_feedbacks = Feedback.objects.filter(teacher__isnull=False, sentiment='neutral').count()

    # Feedback trends over time (example: by month)
    feedback_trends = Feedback.objects.filter(teacher__isnull=False).extra(select={'month': "strftime('%%Y-%%m', created_at)"}).values('month', 'sentiment').annotate(count=Count('id')).order_by('month')

    # Top and bottom rated teachers
    top_teachers = Feedback.objects.filter(teacher__isnull=False,sentiment='positive').values('teacher__fname', 'teacher__lname').annotate(count=Count('id')).order_by('-count')[:5]
    bottom_teachers = Feedback.objects.filter(teacher__isnull=False,sentiment='negative').values('teacher__fname', 'teacher__lname').annotate(count=Count('id')).order_by('-count')[:5]

    # Recent feedback
    recent_feedback = Feedback.objects.filter(teacher__isnull=False).order_by('-created_at')[:10]

    #form lTeacher
    form = TeacherForm()

    #
    teachers=Teacher.objects.all()
    context = {
        'total_teachers': total_teachers,
        'positive_feedback': total_positive_feedbacks,
        'neutral_feedback': total_neutral_feedbacks,
        'negative_feedback': total_negative_feedbacks,
        'feedback_trends': feedback_trends,
        'top_teachers': top_teachers,
        'bottom_teachers': bottom_teachers,
        'recent_feedback': recent_feedback,
        'form': form,
        'teachers':teachers,
    }
    return render(request, 'theme/teacherAn.html', context)


#add teacher 

def add_teacher(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('teacherAn')  # Redirect to a view that lists teachers after successful submission

def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    teacher.delete()
    return redirect('teacherAn')  

def courseAn(request):

    total_courses=Course.objects.count()
    total_positive_feedbacks = Feedback.objects.filter(course__isnull=False, sentiment='positive').count()
    total_negative_feedbacks = Feedback.objects.filter(course__isnull=False, sentiment='negative').count()
    total_neutral_feedbacks = Feedback.objects.filter(course__isnull=False, sentiment='neutral').count()

    feedback_trends = Feedback.objects.filter(course__isnull=False).extra(select={'month': "strftime('%%Y-%%m', created_at)"}).values('month', 'sentiment').annotate(count=Count('id')).order_by('month')

    # Top and bottom rated courses
    top_courses = Feedback.objects.filter(course__isnull=False,sentiment='positive').values('course__name').annotate(count=Count('id')).order_by('-count')[:5]
    bottom_courses = Feedback.objects.filter(course__isnull=False,sentiment='negative').values('course__name').annotate(count=Count('id')).order_by('-count')[:5]

    # Recent feedback
    recent_feedback = Feedback.objects.filter(course__isnull=False).order_by('-created_at')[:10]

    #form lcourse
    form = CourseForm()

    courses=Course.objects.all()
    

    context={
        'total_courses':total_courses,
        'positive_feedback': total_positive_feedbacks,
        'neutral_feedback': total_neutral_feedbacks,
        'negative_feedback': total_negative_feedbacks,
        'feedback_trends': feedback_trends,
        'top_courses': top_courses,
        'bottom_courses': bottom_courses,
        'recent_feedback': recent_feedback,
        'form': form,
        'courses':courses,
    }

    return render(request,'theme/courseAn.html',context)



def addCourse(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('courseAn')
        

def delete_course(request, course_id):
    teacher = get_object_or_404(Course, id=course_id)
    teacher.delete()
    return redirect('courseAn')


def studentAn(request):
    total_feedbacks = Feedback.objects.count()
    form = StudentForm()
    # Calculate sentiment counts
    positive_feedbacks = Feedback.objects.filter(sentiment='positive').count()
    negative_feedbacks = Feedback.objects.filter(sentiment='negative').count()
    neutral_feedbacks = Feedback.objects.filter(sentiment='neutral').count()
    
    # Map sentiments to numerical values
    sentiment_mapping = {
        'positive': 1,
        'neutral': 0,
        'negative': -1
    }
    
    # Calculate average sentiment per student
    feedbacks = Feedback.objects.all()
    student_sentiments = {}
    for feedback in feedbacks:
        student = f"{feedback.student.fname} {feedback.student.lname}"
        if student not in student_sentiments:
            student_sentiments[student] = []
        student_sentiments[student].append(sentiment_mapping[feedback.sentiment])
    
    student_sentiment_avg = {student: sum(scores) / len(scores) for student, scores in student_sentiments.items()}
    sorted_student_sentiment = sorted(student_sentiment_avg.items(), key=lambda x: x[1], reverse=True)
    
    # Generate word clouds
    positive_feedback_text = ' '.join(Feedback.objects.filter(sentiment='positive').values_list('content', flat=True))
    negative_feedback_text = ' '.join(Feedback.objects.filter(sentiment='negative').values_list('content', flat=True))
    
    def generate_wordcloud(text):
        wordcloud = WordCloud(width=500, height=400, background_color='white').generate(text)
        image = io.BytesIO()
        wordcloud.to_image().save(image, format='PNG')
        return base64.b64encode(image.getvalue()).decode('utf-8')
    
    positive_wordcloud = generate_wordcloud(positive_feedback_text)
    negative_wordcloud = generate_wordcloud(negative_feedback_text)
    
    # Calculate overall sentiment
    overall_sentiment_score = sum(sentiment_mapping[f.sentiment] for f in feedbacks) / len(feedbacks)
    
    if overall_sentiment_score > 0.2:
        sentiment_summary = "Students are feeling good."
        sentiment_color = "green"
    elif overall_sentiment_score < -0.2:
        sentiment_summary = "Students are feeling bad."
        sentiment_color = "red"
    else:
        sentiment_summary = "Students are feeling neutral."
        sentiment_color = "orange"
    
    # Predict sentiment trend (simple moving average)
    today = date.today()
    one_year_ago = today - relativedelta(years=1)
    
    feedbacks_last_year = Feedback.objects.filter(created_at__range=(one_year_ago, today))
    
    sentiment_trend = feedbacks_last_year.extra(
        select={'month': "strftime('%%m', created_at)"}
    ).values('month').annotate(
        positive=Count('id', filter=Q(sentiment='positive')),
        negative=Count('id', filter=Q(sentiment='negative')),
        neutral=Count('id', filter=Q(sentiment='neutral'))
    ).order_by('month')
    students = Student.objects.all()
    context = {
        'total_feedbacks': total_feedbacks,
        'positive_feedback': positive_feedbacks,
        'negative_feedback': negative_feedbacks,
        'neutral_feedback': neutral_feedbacks,
        'student_sentiment': sorted_student_sentiment,
        'positive_wordcloud': positive_wordcloud,
        'negative_wordcloud': negative_wordcloud,
        'sentiment_summary': sentiment_summary,
        'sentiment_color': sentiment_color,
        'sentiment_trend': sentiment_trend,
        'form': form,
        'students': students,
    }
    
    return render(request, 'theme/studentSntAn.html', context)


def profile(request):
    profile = Profile.objects.get(username=request.session['username'])

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
                profile.password = make_password(new_password)

            if new_username and new_username != profile.username:
                if Profile.objects.filter(username=new_username).exists():
                    messages.error(request, "Username already exists.")
                else:
                    profile.username = new_username

            if new_email and new_email != profile.email:
                if Profile.objects.filter(email=new_email).exists():
                    messages.error(request, "Email already exists.")
                else:
                    profile.email = new_email

            profile.save()
            messages.success(request, "Profile successfully updated.")
            return redirect('profile')

    return render(request, 'theme/profile.html', {'student': profile})


#to do 

def todo_list(request):
    profile = Profile.objects.get(username=request.session['username'])
    todos = profile.todos.all()
    return render(request, 'theme/todo_list.html', {'todos': todos})

def add_todo(request):
    if request.method == 'POST':
        profile = Profile.objects.get(username=request.session['username'])
        task = request.POST.get('task')
        if task:
            Todo.objects.create(profile=profile, task=task)
            messages.success(request, 'To-do item added successfully.')
        else:
            messages.error(request, 'To-do item cannot be empty.')
    return redirect('todo_list')

def delete_todo(request, todo_id):
    todo = Todo.objects.get(id=todo_id)
    if todo.profile.username == request.session['username']:
        todo.delete()
        messages.success(request, 'To-do item deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this item.')
    return redirect('todo_list')


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()

    return redirect('studentAn')        
    

def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        student.delete()
        return redirect('studentAn')
    
def addStudent(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('studentAn')
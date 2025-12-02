
from django.urls import path
from . import views
urlpatterns = [
    path('',views.log,name="student-login"),
    path('student/dashboard/',views.dashboard_view,name="studentDashboard"),
    path('predict-sentiment/', views.predict_feedback_sentiment, name='predict_sentiment'),
    path('teachers/', views.list_teachers, name='list_teachers'),
    path('courses/', views.list_courses, name='list_courses'),
    path('teachers/feedback/<int:teacher_id>/', views.submit_teacher_feedback, name='submit_teacher_feedback'),
    path('courses/feedback/<int:course_id>/', views.submit_course_feedback, name='submit_course_feedback'),
     path('profile/',views.profile,name="profileSt"),
     path('logout/',views.logout,name="logoutSt"),
]
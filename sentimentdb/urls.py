
from django.urls import path
from . import views
urlpatterns = [
    path('',views.log,name="page-login"),
    path('dashboard/',views.dashboard_view,name="dashboard"),
    path('logout/',views.logout,name="logout"),
    path('teachersAnalytics/',views.teacherAn,name="teacherAn"),
    path('add_teacher/', views.add_teacher, name='add_teacher'),
    path('delete_teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),

    path('CoursesAnalytics',views.courseAn,name="courseAn"),
    path('add_course/',views.addCourse,name="add_course"),
    path('delete_course/<int:course_id>/', views.delete_course, name='delete_course'),
    path('studentsAnalytics/',views.studentAn,name="studentAn"),
    path('profile/',views.profile,name="profile"),
    path('todos/', views.todo_list, name='todo_list'),
    path('add-todo/', views.add_todo, name='add_todo'),
    path('delete-todo/<int:todo_id>/', views.delete_todo, name='delete_todo'),
    path('edit_student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('add_student/',views.addStudent,name="add_student"),
]
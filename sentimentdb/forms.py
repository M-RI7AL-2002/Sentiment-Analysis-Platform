from django import forms
from .models import Teacher,Course
from studentdb.models import Student
class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['fname', 'lname', 'email']


class CourseForm(forms.ModelForm):
    class Meta:
        model=Course
        fields=['name']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['fname', 'lname', 'email','username','password']

        widgets = {
            'password': forms.PasswordInput(),
        }
        
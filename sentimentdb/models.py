from django.db import models
from studentdb.models import Student

from django.contrib.auth.hashers import make_password
# Create your models here.
from django.core.exceptions import ValidationError

from django.core.exceptions import ValidationError

class Profile(models.Model):
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def save(self, *args, **kwargs):
        # Retrieve the original password from the database if the instance already exists
        if self.pk is not None:
            original = Profile.objects.get(pk=self.pk)
            if self.password != original.password:
                self.password = make_password(self.password)
        else:
            self.password = make_password(self.password)
        super(Profile, self).save(*args, **kwargs)

    def clean(self):
        if Profile.objects.exclude(pk=self.pk).filter(username=self.username).exists():
            raise ValidationError({'username': "Username already exists."})
        if Profile.objects.exclude(pk=self.pk).filter(email=self.email).exists():
            raise ValidationError({'email': "Email already exists."})

    def __str__(self):
        return self.username

   
    class Meta:
        verbose_name='Profiles'


class Teacher(models.Model):
  
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.fname +" "+ self.lname

class Course(models.Model):
   
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Feedback(models.Model):

    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]


    content = models.TextField()
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)  # Positive, Neutral, Negative
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 


    def __str__(self):
         return f"Feedback by {self.student} on {self.created_at}"
    


class Todo(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='todos')
    task = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.task

   
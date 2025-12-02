from django.db import models

# Create your models here.
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
class Student(models.Model):
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def save(self, *args, **kwargs):
        # Retrieve the original password from the database if the instance already exists
        if self.pk is not None:
            original = Student.objects.get(pk=self.pk)
            if self.password != original.password:
                self.password = make_password(self.password)
        else:
            self.password = make_password(self.password)
        super(Student, self).save(*args, **kwargs)

    def clean(self):
        if Student.objects.exclude(pk=self.pk).filter(username=self.username).exists():
            raise ValidationError({'username': "Username already exists."})
        if Student.objects.exclude(pk=self.pk).filter(email=self.email).exists():
            raise ValidationError({'email': "Email already exists."})

    def __str__(self):
        return self.username
    class Meta:
        verbose_name='Students'
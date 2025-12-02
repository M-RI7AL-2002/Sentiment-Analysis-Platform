from django.contrib import admin
from .models import Profile ,Teacher,Course,Feedback
# Register your models here.
admin.site.register(Profile)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(Feedback)

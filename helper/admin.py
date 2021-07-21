from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Profile)
admin.site.register(Group)
admin.site.register(Schedule)
admin.site.register(GroupAssignment)
admin.site.register(SubAssignment)
admin.site.register(Blog)
admin.site.register(Comment)
admin.site.register(Friend)
admin.site.register(Collection)
from django.urls import path
from .views import user


app_name = 'helper'
urlpatterns = [
    path('register/', user.register, name='register'),
    path('', user.login, name='login'),
    path('user/<int:pk>/homepage/', user.homepage, name='homepage'),
    path('user/<int:pk>/pwd_change/', user.pwd_change, name='pwd_change'),
    path('logout/', user.logout, name='logout'),
]

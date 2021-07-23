from django.urls import path
from .views import user, blog


app_name = 'helper'
urlpatterns = [
    path('register/', user.register, name='register'),
    path('login/', user.login, name='login'),
    path('', user.index, name='index'),
    path('user/<int:pk>/homepage/', user.homepage, name='homepage'),
    path('user/<int:pk>/blog_homepage/', blog.blog_homepage, name='blog_homepage'),
    path('user/<int:pk>/pwd_change/', user.pwd_change, name='pwd_change'),
    path('logout/', user.logout, name='logout'),
]

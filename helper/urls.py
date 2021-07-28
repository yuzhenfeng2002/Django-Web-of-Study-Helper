from django.urls import path
from .views import user, blog, group


app_name = 'helper'
urlpatterns = [
    path('register/', user.register, name='register'),
    path('login/', user.login, name='login'),
    path('', user.index, name='index'),
    path('user/home/', user.home, name='home'),
    path('user/pwd_change/', user.pwd_change, name='pwd_change'),
    path('user/friends_admin/', user.friends_admin, name='friends_admin'),
    path('blog/home/', blog.home, name='blog_homepage'),
    path('blog/hot/<int:pg>', blog.hot, name='hot'),
    path('blog/<int:pk>/modify', blog.modify, name='blog_modify'),
    path('blog/<int:pk>/delete', blog.delete, name='blog_delete'),
    path('blog/add', blog.add, name='blog_add'),
    path('blog/<int:pk>/', blog.blog, name='blog_page'),
    path('blog/friend/<int:friend_id>/', blog.public, name='public'),
    path('logout/', user.logout, name='logout'),
    path('group/', group.group_admin, name='group_admin'),
    path('group/<int:pk>/', group.home, name='group_home'),
    path('group/<int:pk>/add_assign/', group.add_assign, name='assign_add'),
    path('group/<int:pk>/add_sub_assign/', group.add_sub_assign, name='sub_assign_add'),
]

from django import forms
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from ..models import *
from .settings import *
import datetime
import math


class ModifyForm(forms.Form):
    title = forms.CharField(label='标题', max_length=50,
                            widget=forms.TextInput(attrs={'class': 'form-control form-control-user mb-5'}))
    content = forms.CharField(label='博客内容', widget=forms.Textarea(attrs={'class': 'form-control form-control-user mb-5'}))


@login_required
def home(request):
    user = request.user

    blogs = Blog.objects.filter(user_id__exact=user.id).order_by('-modified_time')
    collections = Collection.objects.filter(user_id__exact=user.id).order_by('-blog__collect_amount')
    return render(request, '../templates/blog/home.html',
                  {
                      'blogs': blogs,
                      'collections': collections
                  })


@login_required
def blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    user: User = request.user
    if user.collection_set.filter(blog_id__exact=blog.pk).count() == 0:
        is_collected = False
    else:
        is_collected = True
    comments = blog.comment_set.all().order_by('created_time')
    if request.method == 'POST':
        delete_comment = request.POST.get('delete_comment')
        create_comment = request.POST.get('create_comment')
        collect_blog = request.POST.get('collect_blog')
        if not (delete_comment is None):
            try:
                comment = Comment.objects.filter(user_id__exact=user.id,
                                                 blog_id__exact=blog.id,
                                                 content__exact=delete_comment)[0]
                comment.delete()
            except IndexError:
                pass

        if not (collect_blog is None):
            collection = Collection.objects.filter(user_id__exact=user.id, blog_id__exact=blog.id)
            if len(collection) == 0:
                new_collection = Collection(user=user, blog=blog)
                blog.collect_amount += 1
                blog.save()
                new_collection.save()
                is_collected = True
            else:
                collection.delete()
                is_collected = False

        if not (create_comment is None):
            new_comment = Comment(user=user, blog=blog, content=create_comment)
            new_comment.save()
    else:
        blog.pageview += 1
        blog.save()

    return render(request, '../templates/blog/blog.html',
                  {'blog': blog, 'comments': comments, 'user': user, 'is_collected': is_collected})


@login_required
def modify(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if blog.user != request.user:
        return HttpResponseForbidden

    if request.method == "POST":
        form = ModifyForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            blog.title = title
            blog.content = content
            blog.save()
            return HttpResponseRedirect(reverse('helper:blog_page', args=(blog.id,)))
    else:
        form = ModifyForm(initial={'title': blog.title, 'content': blog.content})

    return render(request, '../templates/blog/modify.html', {'form': form})


@login_required
def delete(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if blog.user != request.user:
        return HttpResponseForbidden
    blog.delete()
    return HttpResponseRedirect(reverse("helper:blog_homepage"))


@login_required
def add(request):
    user = request.user

    if request.method == "POST":
        form = ModifyForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            blog = Blog(user=user, title=title, content=content)
            blog.save()
            return HttpResponseRedirect(reverse('helper:blog_page', args=(blog.id,)))
    else:
        form = ModifyForm()

    return render(request, '../templates/blog/modify.html', {'form': form})


def hot(request, pg):
    blogs = Blog.objects.filter(Q(user__blog__pageview__gte=HOT_BLOG_PAGEVIEW,
                                  modified_time__gte = timezone.now() -
                                                       datetime.timedelta(days=BLOGPAGE_HOT_BLOG_DAY)) |
                                Q(modified_time__gte = timezone.now() -
                                                       datetime.timedelta(days=BLOGPAGE_COMMON_BLOG_DAY))).distinct().order_by('-modified_time')
    page_num = math.ceil(len(blogs) / BLOGPAGE_BLOG_NUMBER)
    if pg > page_num or pg < 1:
        return HttpResponseNotFound()

    if pg * BLOGPAGE_BLOG_NUMBER > len(blogs):
        number = len(blogs)
    else:
        number = pg * BLOGPAGE_BLOG_NUMBER

    blogs = blogs[(pg - 1) * BLOGPAGE_BLOG_NUMBER: number]
    return render(request, '../templates/blog/hot.html',
                  {
                      'blogs': blogs,
                      'page_num': page_num,
                      'current_page': pg
                  })


@login_required
def public(request, friend_id):
    user: User = request.user
    friend = Friend.objects.filter(user_id__exact=user.id, friend_id__exact=friend_id)
    if len(friend) == 0 and friend_id != user.id:
        return HttpResponseForbidden()
    blogs = Blog.objects.filter(user_id__exact=friend_id)
    message = None
    if friend_id == user.id:
        friend_user = user
    else:
        friend_user = friend[0].friend
        if friend[0].authority == 0:
            blogs = None
            message = "没有权限访问！"

    return render(request, '../templates/blog/friend.html',
                  {
                      'blogs': blogs,
                      'friend': friend_user,
                      'message': message
                  })

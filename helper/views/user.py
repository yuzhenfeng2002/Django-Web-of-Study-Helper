from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from ..models import Profile
from django import forms
from django.contrib import auth
import re


class RegistrationForm(forms.Form):
    TYPE_CHOICES = [('S', '学生'), ('T', '教师')]
    GENDER_CHOICES = [('M', '男'), ('F', '女')]

    user_id = forms.CharField(label='学/工号', max_length=7)
    email = forms.EmailField(label='邮箱')
    user_name = forms.CharField(label='昵称', max_length=10)
    gender = forms.ChoiceField(label='性别', widget=forms.RadioSelect, choices=GENDER_CHOICES)
    user_type = forms.ChoiceField(label='用户类型', widget=forms.RadioSelect, choices=TYPE_CHOICES)
    class_name = forms.CharField(label='班级', max_length=20, required=False)
    password1 = forms.CharField(label='密码', widget=forms.PasswordInput)
    password2 = forms.CharField(label='再次输入密码', widget=forms.PasswordInput)

    def clean_user_id(self):
        user_id = self.cleaned_data.get('user_id')
        user_type = self.cleaned_data.get('user_type')
        if user_type == 'S' and len(user_id) != 7:
            raise forms.ValidationError("请输入有效的学号。")
        elif user_type == 'T' and len(user_id) != 5:
            raise forms.ValidationError("请输入有效的工号。")
        else:
            filter_result = User.objects.filter(username__exact=user_id)
            if len(filter_result) > 0:
                raise forms.ValidationError("您的学/工号已被注册过。")
            return user_id

    def clean_email(self):
        pattern = re.compile(r"\"?([-a-zA-Z0-9.'?{}]+@\w+\.\w+)\"?")
        email = self.cleaned_data.get('email')
        if re.match(pattern, email):
            filter_result = User.objects.filter(email__exact=email)
            if len(filter_result) > 0:
                raise forms.ValidationError("您的邮箱已被注册过。")
        else:
            raise forms.ValidationError("请输入有效的邮箱。")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) <= 6:
            raise forms.ValidationError("您的密码太短，请重新输入。")
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('两次输入的密码不一致，请重新输入')
        return password2


class LoginForm(forms.Form):
    email = forms.EmailField(label='邮箱')
    password = forms.CharField(label='密码', widget=forms.PasswordInput)

    def clean_email(self):
        pattern = re.compile(r"\"?([-a-zA-Z0-9.'?{}]+@\w+\.\w+)\"?")
        email = self.cleaned_data.get('email')
        if re.match(pattern, email):
            filter_result = User.objects.filter(email__exact=email)
            if len(filter_result) == 0:
                raise forms.ValidationError("邮箱不存在。")
        else:
            raise forms.ValidationError("请输入有效的邮箱。")
        return email


class PwdChangeForm(forms.Form):
    old_password = forms.CharField(label='旧的密码', widget=forms.PasswordInput)

    password1 = forms.CharField(label='密码', widget=forms.PasswordInput)
    password2 = forms.CharField(label='再次输入密码', widget=forms.PasswordInput)

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) <= 6:
            raise forms.ValidationError("您的密码太短，请重新输入。")
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('两次输入的密码不一致，请重新输入')
        return password2


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            user_name = form.cleaned_data['user_name']
            email = form.cleaned_data['email']
            gender = form.cleaned_data['gender']
            user_type = form.cleaned_data['user_type']
            class_name = form.cleaned_data['class_name']
            password = form.cleaned_data['password1']

            user = User.objects.create_user(username=user_id, password=password, email=email)

            user_profile = Profile(class_name=class_name, type=user_type, gender=gender, user=user, name=user_name)
            user_profile.save()

            return HttpResponseRedirect(reverse("helper:login"))
    else:
        form = RegistrationForm()
    return render(request, '../templates/user/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.filter(email__exact=email)
            user_id = user.get().username
            user = auth.authenticate(username=user_id, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('helper:homepage', args=(user.id,)))
            else:
                return render(request, '../templates/user/login.html',
                              {'form': form, 'message': '密码错误，请重新输入！'})
    else:
        form = LoginForm()
    return render(request, '../templates/user/login.html', {'form': form})


@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse("helper:login"))


@login_required
def pwd_change(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        form = PwdChangeForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['old_password']
            username = user.username

            user = auth.authenticate(username=username, password=password)

            if user is not None and user.is_active:
                new_password = form.cleaned_data['password2']
                user.set_password(new_password)
                user.save()
                return HttpResponseRedirect(reverse('helper:login'))

            else:
                return render(request, '../templates/user/pwd_change.html',
                              {'form': form, 'user': user, 'message': '旧密码错误！'})
    else:
        form = PwdChangeForm()

    return render(request, '../templates/user/pwd_change.html', {'form': form, 'user': user})


@login_required
def homepage(request, pk):
    user = get_object_or_404(User, pk=pk)
    schedule = user.schedule_set.get()
    return render(request, '../templates/user/homepage.html', {'user': user, 'schedule': schedule})
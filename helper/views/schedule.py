from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.forms import Form
from django.forms import fields
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from helper import models
import datetime
import copy
from .settings import *


class TodoForm(Form):
    CYCLE_CHOICES = (
        ('N', '不重复'),
        ('D', '每天'),
        ('W', '每周'),
        ('M', '每月')
    )
    REPEAT_CYCLE = (
        (False, '不重复'),
        (True, '重复')
    )
    description = fields.CharField(label='日程描述', required=True, max_length=50,
                                   widget=forms.TextInput(attrs={
                                       'class': 'form-control form-control-user mb-5'
                                   }))
    type = fields.CharField(label='日程类型', required=True, max_length=2,
                            widget=forms.TextInput(attrs={'class': 'form-control form-control-user mb-5'}))
    weight = fields.IntegerField(label='权重', required=True, max_value=100,
                                 widget=forms.NumberInput(attrs={'class': 'form-control form-control-user mb-5'}))
    is_repeated = fields.ChoiceField(label='是否重复', choices=REPEAT_CYCLE, widget=forms.RadioSelect)
    repeat_cycle = fields.ChoiceField(label='重复周期', required=False, choices=CYCLE_CHOICES, widget=forms.RadioSelect)
    start_time = fields.DateTimeField(label='开始时间', required=True,
                                      widget=forms.DateTimeInput(attrs={'class': 'form-control form-control-user mb-5'}))
    deadline = fields.DateTimeField(label='截止时间', required=True,
                                    widget=forms.DateTimeInput(attrs={'class': 'form-control form-control-user mb-5'}))
    expected_minutes_consumed = fields.IntegerField(label='预期花费时间', required=False,
                                                    widget=forms.NumberInput(
                                                        attrs={'class': 'form-control form-control-user mb-5'}))


@login_required
def add_todo_list(request):
    if request.method == "GET":
        form = TodoForm()
        return render(request, "../templates/schedule/add_schedule.html", {'form': form})
    else:
        form = TodoForm(request.POST)
        if form.is_valid():
            user = request.user
            description = form.cleaned_data['description']
            type = form.cleaned_data['type']
            is_repeated = form.cleaned_data['is_repeated']
            repeat_cycle = form.cleaned_data['repeat_cycle']
            if repeat_cycle == 'N':
                repeat_cycle = None
            start_time = form.cleaned_data['start_time']
            weight = form.cleaned_data['weight']
            deadline = form.cleaned_data['deadline']
            emc = form.cleaned_data['expected_minutes_consumed']
            models.Schedule.objects.create(user_id=user.id, description=description, type=type, is_repeated=is_repeated,
                                           is_done=False, start_time=start_time, weight=weight, deadline=deadline,
                                           expected_minutes_consumed=emc, repeat_cycle=repeat_cycle)
            return HttpResponseRedirect(reverse("helper:schedule_home"))
        else:
            message = "添加失败！"
            return render(request, "../templates/schedule/add_schedule.html", {'form': form, 'message': message})


def get_schedules(user, search_day_num):
    schedule_not_repeated = user.schedule_set.filter(is_done__exact=False, is_repeated__exact=False)
    schedule_daily = user.schedule_set.filter(is_repeated__exact=True, repeat_cycle__exact='D',
                                              deadline__gte=timezone.now())
    schedule_weekly = user.schedule_set.filter(is_repeated__exact=True, repeat_cycle__exact='W',
                                               deadline__gte=timezone.now())
    schedule_monthly = user.schedule_set.filter(is_repeated__exact=True, repeat_cycle__exact='M',
                                                deadline__gte=timezone.now())

    def update_time(s, i, schedules):
        time = datetime.datetime.now() + datetime.timedelta(days=i)
        if i == 0:
            finish_time_range = (
                datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time()),
                datetime.datetime.combine(datetime.date.today(), datetime.datetime.max.time())
            )
            if len(models.FinishedSchedule.objects.filter(finish_time__range=finish_time_range, schedule_id=s.id)) != 0:
                return

        interval = time.date() - s.start_time.date()
        s.start_time += datetime.timedelta(days=interval.days)
        schedules.append(s)

    schedules = list(schedule_not_repeated)
    for i in range(search_day_num):
        time = datetime.datetime.now() + datetime.timedelta(days=i)
        for j in range(len(schedule_daily)):
            s = copy.copy(schedule_daily[j])
            update_time(s, i, schedules)
        for j in range(len(schedule_weekly)):
            s = copy.copy(schedule_weekly[j])
            if s.start_time.weekday() == time.weekday():
                update_time(s, i, schedules)
        for j in range(len(schedule_monthly)):
            s = copy.copy(schedule_monthly[j])
            if s.start_time.day == time.day:
                update_time(s, i, schedules)
    schedules.sort(key=lambda sc: sc.start_time)
    return schedules


@login_required
def home(request):
    user = request.user
    search_day_num = HOMEPAGE_SCHEDULE_DAY
    if request.method == 'POST':
        day_num = request.POST.get('search_day_num')
        finish_id = request.POST.get('finish_id')
        time_consumed = request.POST.get('time_consumed')
        if not (day_num is None):
            search_day_num = int(day_num)
        if not (finish_id is None):
            schedule = models.Schedule.objects.filter(id=finish_id)[0]
            if not schedule.is_repeated:
                models.FinishedSchedule.objects.create(schedule_id=finish_id)
                schedule.is_done = True
                schedule.save()
            elif not (time_consumed is None):
                models.FinishedSchedule.objects.create(schedule_id=finish_id, minutes_consumed=time_consumed)
            else:
                models.FinishedSchedule.objects.create(schedule_id=finish_id)

    schedules = get_schedules(user, search_day_num)
    daily_schedules = get_schedules(user, 1)
    for ds in daily_schedules:
        if ds.is_repeated == True:
            ds.deadline = ds.start_time + datetime.timedelta(minutes=ds.expected_minutes_consumed)
    return render(request, "../templates/schedule/home.html",
                  {
                      'schedules': schedules,
                      'day_num': search_day_num,
                      'daily_schedules': daily_schedules
                  })


@login_required
def daily_schedules(request):
    user = request.user
    if request.method == 'POST':
        finish_id = request.POST.get('finish_id')
        time_consumed = request.POST.get('time_consumed')
        if not (finish_id is None):
            schedule = models.Schedule.objects.filter(id=finish_id)[0]
            if not schedule.is_repeated:
                models.FinishedSchedule.objects.create(schedule_id=finish_id)
                schedule.is_done = True
                schedule.save()
            elif not (time_consumed is None):
                models.FinishedSchedule.objects.create(schedule_id=finish_id, minutes_consumed=time_consumed)
            else:
                models.FinishedSchedule.objects.create(schedule_id=finish_id)
    schedules = get_schedules(user, 1)
    for s in schedules:
        if s.is_repeated:
            s.deadline = s.start_time + datetime.timedelta(minutes=s.expected_minutes_consumed)
    return render(request, "../templates/schedule/daily_schedules.html", {'schedules': schedules})

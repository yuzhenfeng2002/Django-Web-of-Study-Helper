from django.shortcuts import render, get_object_or_404
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from helper import models


class SubAssignmentForm(forms.Form):
    description = forms.CharField(label='子任务描述', required=True, max_length=50)
    pre_sub_assignment = forms.CharField(label='前置子任务', required=False, max_length=50)
    start_time = forms.DateTimeField(label='开始时间', required=True)
    deadline = forms.DateTimeField(label='截止日期', required=True)
    user = forms.ModelChoiceField(label='用户', queryset=User.objects.all(), required=True)
    assignment = forms.ModelChoiceField(label='父任务', queryset=models.GroupAssignment.objects.all(), required=True)
    weight = forms.IntegerField(label='权重', required=True, max_value=100)
    expected_minutes_consumed = forms.IntegerField(label='预期花费时间', required=True)


class GroupForm(forms.Form):
    type = forms.CharField(label='小组类型', required=True, max_length=20)
    group_name = forms.CharField(label='小组名称', required=True, max_length=20)


class AssignmentForm(forms.Form):
    description = forms.CharField(label='任务描述', required=True, max_length=1000)
    deadline = forms.DateTimeField(label='截止日期', required=True)


@login_required
def group_admin(request):
    user = request.user
    leader_groups = None
    if request.method == 'POST':
        add_group = request.POST.get('add')
        leader_id = request.POST.get('leader_id')
        group_id = request.POST.get('group_id')
        if not(add_group is None):
            type = request.POST.get('type')
            name = request.POST.get('group_name')
            group = models.Group(type=type, group_name=name, leader=user)
            group.save()
            models.UserGroup.objects.create(is_leader=True, group=group, user=user)

        if not(leader_id is None):
            leader = models.User.objects.filter(username=leader_id)[0]
            leader_groups = models.Group.objects.filter(leader_id__exact=leader.id)

        if not(group_id is None):
            if models.UserGroup.objects.filter(pk=group_id, user_id=user.id).count() == 0:
                user_group = models.UserGroup(is_leader=False, group_id=group_id, user=user)
                print(user_group)
                user_group.save()

    add_form = GroupForm()
    user_groups = models.UserGroup.objects.filter(user_id=user.id)
    groups = list(map(lambda k: k.group, user_groups))

    return render(request, '../templates/group/groups_admin.html',
                  {
                      'add_form': add_form,
                      'groups': groups,
                      'leader_groups': leader_groups
                  })


@login_required
def add_sub_assign(request, pk):
    user = request.user
    group = get_object_or_404(models.Group, pk=pk)
    if user.id != group.leader.id:
        return HttpResponseForbidden
    if request.method == "GET":
        form = SubAssignmentForm()
        qs_user = User.objects.filter(usergroup__group_id=group.id)
        qs_assign = models.GroupAssignment.objects.filter(group_id=group.id).distinct()
        form.fields['user'].queryset = qs_user
        form.fields['assignment'].queryset = qs_assign
        return render(request, "../templates/group/add_sub_assign.html", {'form': form})
    else:
        form = SubAssignmentForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['user']
            user = User.objects.filter(username=username)[0]
            assignment_id = models.GroupAssignment.objects.filter(group=group,
                                                                  description=form.cleaned_data['assignment'])[0].id
            description = form.cleaned_data['description']
            deadline = form.cleaned_data['deadline']
            weight = form.cleaned_data['weight']
            pre_sub_assignment = form.cleaned_data['pre_sub_assignment']
            emc = form.cleaned_data['expected_minutes_consumed']
            start_time = form.cleaned_data['start_time']

            models.SubAssignment.objects.create(assignment_id=assignment_id,
                                                pre_sub_assignment=pre_sub_assignment,
                                                user_id=user.id,
                                                description=description,
                                                weight=weight, deadline=deadline, expected_minutes_consumed=emc)
            models.Schedule.objects.create(user_id=user.id, description=description, type="学习", is_repeated=False,
                                           is_done=False, start_time=start_time, weight=weight, deadline=deadline,
                                           expected_minutes_consumed=emc, process=0)
        return HttpResponseRedirect(reverse('helper:group_home', args=(pk, )))


@login_required
def add_assign(request, pk):
    if request.method == "GET":
        form = AssignmentForm()
        return render(request, "../templates/group/add_assign.html", {'form': form})
    else:
        form = AssignmentForm(request.POST)
        if form.is_valid():
            user = request.user
            group = get_object_or_404(models.Group, pk=pk)
            if user.id != group.leader.id:
                return HttpResponseForbidden
            models.GroupAssignment.objects.create(description=form.cleaned_data['description'],
                                                  deadline=form.cleaned_data['deadline'],
                                                  group_id=pk)
            return HttpResponseRedirect(reverse('helper:group_home', args=(pk, )))
        else:
            return render(request, "../templates/group/add_assign.html", {'message': "添加失败！", 'form': form})


@login_required
def home(request, pk):
    user = request.user
    group = get_object_or_404(models.Group, pk=pk)
    user_group = models.UserGroup.objects.filter(group=group)
    partcipants = list(map(lambda k: k.user.id, user_group))
    if not (user.id in partcipants):
        return HttpResponseForbidden
    assignments = models.GroupAssignment.objects.filter(group=group)
    sub_assignments = models.SubAssignment.objects.filter(assignment__group=group)
    return render(request, '../templates/group/home.html', {
        'group': group,
        'partcipants': user_group,
        'assignments': assignments,
        'sub_assignments': sub_assignments
    })


# @login_required
# def add(request):
#     if request.method == "GET":
#         form = GroupForm()
#         return render(request, "../templates/group/add.html", {'form': form})
#     else:
#         form = GroupForm(request.POST)
#         if form.is_valid():
#             user = request.user
#
#             group = models.Group(type=form.cleaned_data['type'],
#                                  group_name=form.cleaned_data['group_name'],
#                                  leader=user)
#             group.save()
#
#             models.UserGroup.objects.create(is_leader=True,
#                                             group=group,
#                                             user=user)
#
#             return render(request, '../templates/group/add.html', {'form': form})
#         else:
#             return render(request, '../templates/group/add.html', {'form': form, 'message': '表单无效！'})
#
#
# @login_required
# def join(request):
#     if request.method == "GET":
#         groups = models.Group.objects.all()
#         return render(request, "../templates/group/join.html", {'groups': groups})
#     if request.is_ajax():
#         user = request.user
#         group_id = request.POST.get('group_id')
#         status = {'status': None}
#
#         result = models.UserGroup.objects.filter(user=user, group_id=group_id)
#         if result.count() == 0:
#             models.UserGroup.objects.create(is_leader=False, group_id=group_id, user=user)
#             status['status'] = 200
#         else:
#             status['status'] = 400
#         return JsonResponse(status)

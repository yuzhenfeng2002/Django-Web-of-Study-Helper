from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    TYPE_CHOICES = (
        ('S', 'Student'),
        ('T', 'Teacher'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    class_name = models.CharField(max_length=20, blank=True, null=True)


class Group(models.Model):
    users = models.ManyToManyField(User)
    group_name = models.CharField(max_length=20)


class Schedule(models.Model):
    CYCLE_CHOICES = (
        ('D', 'Daily'),
        ('W', 'Weekly'),
        ('M', 'Monthly')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    schedule_id = models.CharField(max_length=5)
    description = models.CharField(max_length=50)
    type = models.CharField(max_length=10)
    is_repeated = models.BooleanField()
    repeat_cycle = models.CharField(max_length=1, choices=CYCLE_CHOICES, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    weight = models.IntegerField(default=1)
    deadline = models.DateTimeField()
    expected_minutes_consumed = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ("user", "schedule_id")


class GroupAssignment(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    assignment_id = models.CharField(max_length=5)
    description = models.TextField()
    deadline = models.DateTimeField()

    class Meta:
        unique_together = ("group", "assignment_id")


class SubAssignment(models.Model):
    assignment = models.ForeignKey(GroupAssignment, on_delete=models.CASCADE)
    sub_assignment_id = models.CharField(max_length=5)
    pre_sub_assignment = models.CharField(max_length=600, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    weight = models.IntegerField(default=1)
    deadline = models.DateTimeField()
    expected_minutes_consumed = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ("assignment", "sub_assignment_id")


class Blog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField()
    pageview = models.IntegerField(default=0)
    collect_amount = models.IntegerField(default=0)


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    comment_id = models.CharField(max_length=5)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        unique_together = ("blog", "comment_id")


class Friend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend")
    authority = models.IntegerField()

    class Meta:
        unique_together = ("user", "friend")


class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    type = models.CharField(max_length=10)

    class Meta:
        unique_together = ("user", "blog")

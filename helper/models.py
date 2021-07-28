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

    def __str__(self):
        return self.user.username


class Group(models.Model):
    id = models.AutoField(primary_key=True)
    group_name = models.CharField(max_length=20)
    type = models.CharField(max_length=20, default="学习")
    leader = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.group_name


class UserGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    is_leader = models.BooleanField()


class Schedule(models.Model):
    CYCLE_CHOICES = (
        ('D', 'Daily'),
        ('W', 'Weekly'),
        ('M', 'Monthly')
    )
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=50)
    type = models.CharField(max_length=10)
    is_repeated = models.BooleanField()
    is_done = models.BooleanField(default=0)
    repeat_cycle = models.CharField(max_length=1, choices=CYCLE_CHOICES, blank=True, null=True)
    start_time = models.DateTimeField()
    weight = models.IntegerField(default=1)
    deadline = models.DateTimeField()
    expected_minutes_consumed = models.IntegerField(blank=True, null=True)
    process = models.DecimalField(max_digits=3, decimal_places=2 , default= 0.00)

    def __str__(self):
        return self.description


class Finished_Schedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    schedule =  models.ForeignKey("Schedule",on_delete=models.CASCADE)
    description = models.CharField(max_length=50)
    type = models.CharField(max_length=10)
    is_repeated = models.BooleanField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    weight = models.IntegerField(default=1)

    def __str__(self):
        return self.description


class Today_Schedule(models.Model):
    schedule =  models.ForeignKey("Schedule",on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=50)
    type = models.CharField(max_length=10)
    is_repeated = models.BooleanField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    spend_time = models.IntegerField()
    weight = models.IntegerField(default=1)
    process = models.DecimalField(  max_digits = 3,decimal_places = 2)

    def __str__(self):
        return self.description


class GroupAssignment(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    description = models.TextField()
    deadline = models.DateTimeField()

    def __str__(self):
        return self.description


class SubAssignment(models.Model):
    assignment = models.ForeignKey(GroupAssignment, on_delete=models.CASCADE)
    pre_sub_assignment = models.CharField(max_length=600, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    weight = models.IntegerField(default=1)
    deadline = models.DateTimeField()
    expected_minutes_consumed = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.description


class Blog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True, auto_now=False)
    modified_time = models.DateTimeField(auto_now_add=False, auto_now=True)
    pageview = models.IntegerField(default=0)
    collect_amount = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return self.content


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

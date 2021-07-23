from django import forms
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from ..models import *
from .settings import *
import re
import datetime
import copy


def blog_homepage(request, pk):
    return HttpResponseRedirect(reverse('helper:homepage', args=(pk,)))

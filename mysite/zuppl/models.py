from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone

class Event(models.Model):
    name = models.CharField(max_length=50)
    created_by = models.CharField(max_length=50)
    created_date = models.DateTimeField('date published', auto_now_add=True)
    location = models.CharField(max_length=50)
    campus = models.CharField(max_length=50)
    start_time = models.DateTimeField('start time')
    end_time = models.DateTimeField('end time')
    cost = models.CharField(max_length=10, default="Free")
    organizer = models.CharField(max_length=50)
    organizer_email = models.EmailField()
    details = models.TextField()

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User)
    college = models.CharField(max_length=50)
    eventset = models.ManyToManyField(Event, related_name="attendees")

    def __str__(self):
        return self.user.get_full_name()

class Comment(models.Model):
    event = models.ForeignKey(Event)
    user = models.ForeignKey(User)
    text = models.TextField()
    post_time = models.DateTimeField('time published', auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('post_time',)
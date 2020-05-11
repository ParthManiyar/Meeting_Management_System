from django.db import models
from django.contrib.auth.models import User
import uuid

#########

def get_uuid():
    return str(uuid.uuid4())

class Venue(models.Model):

    name = models.CharField(max_length=200)
    uuid = models.CharField(max_length=100,default = get_uuid(), editable=False)
    def __str__(self):
        return self.name

#########

class Event(models.Model):

    start_time = models.TimeField()
    end_time   = models.TimeField()
    name       = models.CharField(max_length=200)
    venue      = models.CharField(max_length=200, default="N/A")
    uuid = models.CharField(max_length=100,default = get_uuid(), editable=False)

    def __str__(self):
        return self.name

#########

class DailySchedule(models.Model):

    date   = models.DateField()
    events = models.ManyToManyField(Event)
    uuid = models.CharField(max_length=100,default = get_uuid(), editable=False)

    def __str__(self):
        return self.date
#########

# class Schedule(models.Model):

#     daily_schedules = models.ManyToManyField(DailySchedule)
#     uuid = models.CharField(max_length=100)

#     def __str__(self):
#         return self.schedule_users.all()

#########

class CustomUser(User):

    class Meta:
        verbose_name = "CustomUser"
        verbose_name_plural = "CustomUsers"

    schedule = models.ManyToManyField(DailySchedule,related_name="schedule_users")
    uuid = models.CharField(max_length=100,default = get_uuid(), editable=False)
    dp = models.ImageField(upload_to='',blank=True)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if self.pk==None:
            self.set_password(self.password)
        super(CustomUser, self).save(*args, **kwargs)

#########

class Message(models.Model):

    text   = models.CharField(max_length=1000)
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    time   = models.DateTimeField(auto_now=True)
    uuid   = models.CharField(max_length=100,default = get_uuid(), editable=False)

    def __str__(self):
        return self.text

#########

class ChatRoom(models.Model):

    name     = models.CharField(max_length=200,default="Chat room")
    messages = models.ManyToManyField(Message)
    uuid     = models.CharField(max_length=100,default = get_uuid(), editable=False)

    def __str__(self):
        return self.name

#########

class Resource(models.Model):

    rfile       = models.FileField()
    owner       = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    upload_time = models.DateTimeField(auto_now=True)
    uuid = models.CharField(max_length=100,default = get_uuid(), editable=False)

    def __str__(self):
        return self.rfile.name

#########

class Group(models.Model):

    name         = models.CharField(max_length=200)
    admins       = models.ManyToManyField(CustomUser,related_name="admin")
    members      = models.ManyToManyField(CustomUser,related_name="member")
    created_date = models.DateTimeField(auto_now=True)
    uuid = models.CharField(max_length=100,default = get_uuid(), editable=False)

    def __str__(self):
        return self.name

    def get_created_date(self):
        return self.created_date.strftime('%B %d %Y')

#########

class Meeting(models.Model):

    name         = models.CharField(max_length=200)
    agenda       = models.CharField(max_length=500)
    group        = models.ForeignKey(Group,on_delete=models.CASCADE)
    attendees    = models.ManyToManyField(CustomUser,related_name="attendee")
    meeting_date = models.DateField(blank=True)
    start_time   = models.DateTimeField(blank=True)
    end_time     = models.DateTimeField(blank=True)
    duration     = models.IntegerField(default=1) ##
    venue        = models.CharField(max_length=200, default="N/A")
    resources    = models.ManyToManyField(Resource)
    chatroom     = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now=True)
    uuid = models.CharField(max_length=100,default = get_uuid(), editable=False)

    def __str__(self):
        return self.name

    def get_time(self):
        return self.start_time.strftime('%B %d %Y')
#########


class Notification(models.Model):

    title        = models.CharField(max_length=200)
    content      = models.CharField(max_length=300)
    isRead       = models.BooleanField(default = False)
    target_users = models.ManyToManyField(CustomUser,related_name="notif")
    uuid = models.CharField(max_length=100,default = get_uuid(), editable=False)

    def __str__(self):
        return self.title

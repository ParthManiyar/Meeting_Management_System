from django.db import models
from django.contrib.auth.models import User
import uuid

#########

def get_uuid():
    return str(uuid.uuid4())

class Venue(models.Model):

    name = models.CharField(max_length=200)
    uuid = models.CharField(max_length=100,default = "", editable=False)
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk==None:
            self.uuid = get_uuid()
        super(Venue, self).save(*args, **kwargs)

#########

class Event(models.Model):

    start_time = models.TimeField()
    end_time   = models.TimeField()
    name       = models.CharField(max_length=200)
    description= models.CharField(max_length=200,null=True)
    venue      = models.CharField(max_length=200, default="N/A")
    uuid = models.CharField(max_length=100,default = "", editable=False)

    def __str__(self):
        return self.name

    def get_start_time(self):
        return self.start_time.strftime('%I:%M %p')

    def get_end_time(self):
        return self.end_time.strftime('%I:%M %p')

    def save(self, *args, **kwargs):
        if self.pk==None:
            self.uuid = get_uuid()
        super(Event, self).save(*args, **kwargs)

#########

class DailySchedule(models.Model):

    date   = models.DateField()
    events = models.ManyToManyField(Event)
    uuid = models.CharField(max_length=100,default = "", editable=False)

    def __str__(self):
        return str(self.date)


    def save(self, *args, **kwargs):
        if self.pk==None:
            self.uuid = get_uuid()
        super(DailySchedule, self).save(*args, **kwargs)
#########

class Schedule(models.Model):

    daily_schedules = models.ManyToManyField(DailySchedule)
    uuid = models.CharField(max_length=100)

    def __str__(self):
        return self.uuid

    def save(self, *args, **kwargs):
        if self.pk==None:
            self.uuid = get_uuid()
        super(Schedule, self).save(*args, **kwargs)
#########

class CustomUser(User):

    class Meta:
        verbose_name = "CustomUser"
        verbose_name_plural = "CustomUsers"

    schedule = models.ForeignKey(Schedule,related_name="schedule_users",on_delete=models.CASCADE,null=True)
    uuid = models.CharField(max_length=100,default = "", editable=False)
    dp = models.ImageField(upload_to='',blank=True)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if self.pk==None:
            self.set_password(self.password)
            self.uuid = get_uuid()
        super(CustomUser, self).save(*args, **kwargs)

#########

class Message(models.Model):

    text   = models.CharField(max_length=1000)
    writer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    time   = models.DateTimeField(auto_now=True)
    uuid   = models.CharField(max_length=100,default = "", editable=False)

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        if self.pk==None:
            self.uuid = get_uuid()
        super(Message, self).save(*args, **kwargs)

#########

class ChatRoom(models.Model):

    name     = models.CharField(max_length=200,default="Chat room")
    messages = models.ManyToManyField(Message)
    uuid     = models.CharField(max_length=100,default = "", editable=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk==None:
            self.uuid = get_uuid()
        super(ChatRoom, self).save(*args, **kwargs)

#########

class Resource(models.Model):

    rfile       = models.FileField(upload_to="resources")
    owner       = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name        = models.CharField(max_length=200,blank=True,null=True)
    upload_time = models.DateTimeField(auto_now=True)
    uuid = models.CharField(max_length=100,default = "", editable=False)

    def __str__(self):
        return self.rfile.name

    def save(self, *args, **kwargs):
        if self.pk==None:
            self.uuid = get_uuid()
        super(Resource, self).save(*args, **kwargs)

#########

class Group(models.Model):

    name         = models.CharField(max_length=200)
    admins       = models.ManyToManyField(CustomUser,related_name="admin")
    members      = models.ManyToManyField(CustomUser,related_name="member")
    created_date = models.DateTimeField(auto_now=True)
    uuid = models.CharField(max_length=100,default = "", editable=False)

    def __str__(self):
        return self.name

    def get_created_date(self):
        return self.created_date.strftime('%B %d, %Y')

    def save(self, *args, **kwargs):
        if self.pk==None:
            self.uuid = get_uuid()
        super(Group, self).save(*args, **kwargs)

#########

class Meeting(models.Model):

    name         = models.CharField(max_length=200)
    agenda       = models.CharField(max_length=500)
    group        = models.ForeignKey(Group,on_delete=models.CASCADE)
    attendees    = models.ManyToManyField(CustomUser,related_name="attendee")
    meeting_date = models.DateField(blank=True,null=True)
    start_time   = models.DateTimeField(blank=True,null=True)
    end_time     = models.DateTimeField(blank=True,null=True)
    duration     = models.IntegerField(default=1) ##
    venue        = models.CharField(max_length=200, default="N/A")
    resources    = models.ManyToManyField(Resource)
    chatroom     = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now=True)
    uuid = models.CharField(max_length=100,default = "", editable=False)

    def __str__(self):
        return self.name

    def get_meeting_date(self):
        return self.start_time.strftime('%B %d, %Y')

    def get_start_time(self):
        return self.start_time.strftime('%I:%M %p')

    def get_end_time(self):
        return self.end_time.strftime('%I:%M %p')

    def save(self, *args, **kwargs):
        if self.pk==None:
            self.uuid = get_uuid()
        super(Meeting, self).save(*args, **kwargs)
#########


class Notification(models.Model):

    title        = models.CharField(max_length=200)
    content      = models.CharField(max_length=300)
    meeting      = models.ForeignKey(Meeting,on_delete=models.CASCADE,null=True,blank=True)
    user         = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True)
    uuid = models.CharField(max_length=100,default="", editable=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk==None:
            self.uuid = get_uuid()
        super(Notification, self).save(*args, **kwargs)

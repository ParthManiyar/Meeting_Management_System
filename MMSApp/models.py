from django.db import models
from django.contrib.auth.models import User


#########

class Venue(models.Model):

    name = models.CharField(max_length=200)
    uuid = models.CharField(max_length=100)
    def __str__(self):
        return self.name

#########

class Event(models.Model):

    start_time = models.TimeField()
    end_time   = models.TimeField()
    name       = models.CharField(max_length=200)
    Venue      = models.ForeignKey(Venue, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=100)

    def __str__(self):
        return self.name

#########

class DailySchedule(models.Model):

    date   = models.DateField()
    events = models.ManyToManyField(Event)
    uuid = models.CharField(max_length=100)

    def __str__(self):
        return self.date
#########

class Schedule(models.Model):

    daily_schedules = models.ManyToManyField(DailySchedule)
    uuid = models.CharField(max_length=100)

    def __str__(self):
        return self.schedule_users.all()

#########

class CustomUser(User):

    class Meta:
        verbose_name = "CustomUser"
        verbose_name_plural = "CustomUsers"

    schedule = models.ManyToManyField(Schedule,related_name="schedule_users")
    uuid = models.CharField(max_length=100)
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
    uuid = models.CharField(max_length=100)

    def __str__(self):
        return self.text

#########

class ChatRoom(models.Model):

    name     = models.CharField(max_length=200,default="Chat room")
    messages = models.ManyToManyField(Message)
    uuid = models.CharField(max_length=100)

    def __str__(self):
        return self.name

#########

class Resource(models.Model):

    rfile       = models.FileField()
    owner       = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    upload_time = models.DateTimeField(auto_now=True)
    uuid = models.CharField(max_length=100)

    def __str__(self):
        return self.rfile.name

#########

class Meeting(models.Model):

    name         = models.CharField(max_length=200)
    agenda       = models.CharField(max_length=500)
    admins       = models.ManyToManyField(CustomUser,related_name="meeting_admin")
    invitees     = models.ManyToManyField(CustomUser,related_name="invitee")
    attendees    = models.ManyToManyField(CustomUser,related_name="attendee")
    start_time   = models.DateTimeField()
    end_time     = models.DateTimeField()
    duration     = models.IntegerField() ##
    venue        = models.ForeignKey(Venue, on_delete=models.CASCADE)
    resources    = models.ManyToManyField(Resource)
    chatroom     = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    created_date = models.DateTimeField()
    uuid = models.CharField(max_length=100)

    def __str__(self):
        return self.name

#########

class Group(models.Model):

    name         = models.CharField(max_length=200)
    admins       = models.ManyToManyField(CustomUser,related_name="admin")
    members      = models.ManyToManyField(CustomUser,related_name="member")
    meetings     = models.ManyToManyField(Meeting,related_name="group")
    created_date = models.DateTimeField(auto_now=True)
    uuid = models.CharField(max_length=100)

    def __str__(self):
        return self.name

#########

class Notification(models.Model):

    title        = models.CharField(max_length=200)
    content      = models.CharField(max_length=300)
    isRead       = models.BooleanField(default = False)
    target_users = models.ManyToManyField(CustomUser,related_name="notif")
    uuid = models.CharField(max_length=100)

    def __str__(self):
        return self.title

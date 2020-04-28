from django.db import models
from django.contrib.auth.models import User

class CustomUser(User):

    class Meta:
        verbose_name = "CustomUser"
        verbose_name_plural = "CustomUsers"

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if self.pk==None:
            self.set_password(self.password)
        super(CustomUser, self).save(*args, **kwargs)

#########

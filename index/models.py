from django.db import models
from django.conf import settings
from common.fields import PickledObjectField
user_model_label = settings.AUTH_USER_MODEL

# Create your models here.
class Quest(models.Model):
    date = models.DateField()
    link = models.CharField(max_length=500)
    uid = models.CharField(max_length=200)
    title = models.TextField()
    type = models.CharField(max_length=200)
    question = models.TextField()
    options = PickledObjectField()
    answer = PickledObjectField()
    reason = models.TextField()

    class Meta:
        ordering = ['-date']

    def __unicode__(self):
        return u"{date}<>{title}".format(date=self.date, title=self.title)

class ErrorRecord(models.Model):
    user = models.ForeignKey(user_model_label, related_name="records")
    passed = models.BooleanField(default=False)
    quest = models.ForeignKey("Quest")
    class Meta:
        unique_together = ['user', 'quest']

class DayClearRecord(models.Model):
    user = models.ForeignKey(user_model_label, related_name="clear_records")
    date = models.DateField()

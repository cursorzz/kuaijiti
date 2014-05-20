from django.db import models
from django.conf import settings
user_model_label = settings.AUTH_USER_MODEL

# Create your models here.
class Quest(models.Model):
    date = models.DateField()
    title = models.TextField()
    content = models.TextField()
    type = models.CharField(max_length=200)
    answer = models.CharField(max_length=200)
    reason = models.TextField()

class UserRecord(models.Model):
    user = models.ForeignKey(user_model_label, related_name="records")
    ok = models.IntegerField(default=0)
    quest = models.ForeignKey("Quest", related_name="answers")

    class Meta:
        unique_together = ['user', 'quest']


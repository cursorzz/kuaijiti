#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.db import models
from django.conf import settings
from common.fields import PickledObjectField
user_model_label = settings.AUTH_USER_MODEL

# Create your models here.
class Quest(models.Model):
    QUEST_TYPES = (
            (0, u"未分类题目"),
            (1, u"会计"),
            (2, u"审计"),
            (3, u"税法"),
            (4, u"经济法"),
            (5, u"财务成本管理"),
            (6, u"公司战略与风险管理")
            )
    date = models.DateField()
    link = models.CharField(max_length=500)
    uid = models.CharField(max_length=200)
    title = models.TextField()
    type = models.CharField(max_length=200)
    question = models.TextField()
    options = PickledObjectField()
    answer = PickledObjectField()
    reason = models.TextField()
    q_type = models.IntegerField(choices=QUEST_TYPES, default=0)

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

class Settings(models.Model):
    user = models.OneToOneField(user_model_label, related_name="setting")
    options = PickledObjectField(null=True, blank=True)


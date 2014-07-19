#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from parser import Updater
import datetime


class ParseTest(TestCase):

    def setUp(self):
        self.U = Updater()

    def test_title_date_match(self):
        date  =datetime.date(2014, 07, 19)
        text = '2014年注册会计师考试每日一练免费测试（07.19）'
        self.assertEqual(self.U.is_right_quests_entrance(date, text), True)
    

        



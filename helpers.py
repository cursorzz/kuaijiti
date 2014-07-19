#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quests.settings")

from index.models import Quest
import re 

class JsonDict(dict):
    def __init__(self, old_dict):
        for key in old_dict:
            setattr(self, key, old_dict[key])

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        try:
            return self[key]
        except ValueError:
            return ''


def get_quest_type(quest):
    if isinstance(quest, dict):
        quest = JsonDict(quest)
    title = quest.title
    quest.q_type = 0
    result = re.findall(ur'《(.+)》', title)
    if result:
        for key, value in Quest.QUEST_TYPES:
            if value == result[0]:
                quest.q_type = key
    if quest.q_type == 0:
        print "[ERROR] cant find correct type for quest %s"%quest.uid
    if not isinstance(quest, JsonDict):
        quest.save()

def get_q_types():
    for quest in Quest.objects.all():
        get_quest_type(quest)

def main():
    get_q_types()

if __name__ == '__main__':
    main()

# Create your views here.
from django.views.generic import TemplateView, View
import redis
from hashlib import md5
import json
RANK_GLOBAL = "global"
RANK_WEEK = "week"

RANK_LIST = "rank_info:user_list"

class CacheDB(object):
    client = None
    def connect(self):
        if not self.client or not self.client.ping():
            self.get_client()
        return self.client

    def get_client(self):
        self.client =  redis.StrictRedis(db=5)

    def get_latest_quests(self):
        c = self.connect()
        latest_day = sorted(map(lambda k: int(k.split(':')[1]), c.keys('parse:*')))[-1]
        return self.get_quests_by_day(latest_day)

    def get_sorted_groups(self):
        c = self.connect()
        return sorted(map(lambda k: int(k.split(':')[1]), c.keys('parse:*')), reverse=True)

        
    def get_quests_by_day(self, day):
        c = self.connect()
        urls = c.lrange("parse:%s"%day, 0, 20)
        quests = []
        for u in urls:
            quests.append(self.get_quest_by_link(u))
        return quests

    def get_quest_by_link(self, url):
        if not len(url) == 32:
            sufix = md5(url).hexdigest()
        else:
            sufix = url
        c = self.connect()
        quest = c.hgetall('quest:' + sufix)
        option = quest['options']
        answer = quest['answer']
        quest['options'] = eval(option).items()
        quest['answer'] = eval(answer)
        return quest

            
class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        rdb = CacheDB()
        kwargs['quests'] = rdb.get_latest_quests()
        kwargs['groups'] = rdb.get_sorted_groups()
        #kwargs.update(self.get_common_data())
        #kwargs['recipients'] = self.system_messages()
        return super(IndexView, self).get_context_data(**kwargs)

class QuestView(TemplateView):
    template_name = 'quest.html'

    def get_context_data(self, **kwargs):
        uid = kwargs.get('uid')
        rdb = CacheDB()
        kwargs['quests'] = rdb.get_quests_by_day(uid)
        return super(QuestView, self).get_context_data(**kwargs)

class MarkFailedView(View):
    pass

        #quest = rdb.get_quest_by_link(uid)
        #quest['options'] = eval(quest['options']).items()
        #quest['answer'] = eval(quest['answer'])
        #kwargs['quest'] = quest


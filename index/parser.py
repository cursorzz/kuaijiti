#!/usr/bin/env python
#-*- coding:utf-8 -*-

import mechanize
import re
from bs4 import BeautifulSoup as bs
import datetime
import hashlib
from django.conf import settings
from index.models import Quest
import cPickle as pickle
#from multiprocessing import Process, Pool

ROOT_URL = 'http://www.chinaacc.com/zhucekuaijishi/mryl/qk/'
day_pattern = r'^http://.*/\D+(\d{8}).*'
date_fmt = "%Y%m%d"

import redis

client = redis.StrictRedis(**settings.REDIS_DB)

prefix = 'parse:'
#HTTP Error 404: Not Found http://www.chinaacc.com/zhucekuaijishi/mryl/tu2014030108515426479505.shtml

class Updater(object):
    def __init__(self):
        self.br = mechanize.Browser()

    def get_today_quests(self, date):
        self.br.open(ROOT_URL)
        for link in self.br.links(url_regex=r'^/zhucekuaijishi/mryl\S+.shtml$'):
            date_match = re.match(day_pattern, link.absolute_url).groups()[0]
            if date_match == date.strftime('%Y%m%d'):
                self.get_day_quests(link)

    def get_day_quests(self, link):
        url, absolute_url = link.url, link.absolute_url
        date_match = re.match(day_pattern, absolute_url).groups()[0]
        self.br.open(absolute_url) 
        quests = []
        for l in self.br.links(url_regex=r"^.+zhucekuaijishi/mryl/\w\w%s\d+.shtml$"%(date_match)):
            if 'target' in dict(l.attrs) and re.match(day_pattern, l.absolute_url).groups()[0] == date_match:
                quests.append(l.absolute_url)
        for link in quests:
            self.get_quest_content(link)
        return

    def get_quest_content(self, link, force=False):
        md5 = hashlib.md5(link).hexdigest()
        date_match = re.match(day_pattern, link).groups()[0]
        date = datetime.datetime.strptime(date_match, date_fmt)
        try:
            info = {'options': {}}
            info['link'] = link
            info['date'] = date
            info['uid'] = md5
            self.br.open(link)
            page = bs(self.br.response().read())
            info['title'] = page.select(".news_content h1")[0].text
            show_button = page.select('#fontzoom p input[type=button]')[0]
            quest = show_button.parent.find_previous_siblings('p')
            quest.reverse()
            for q in quest:
                if q.select('script'):
                    quest.remove(q)
            info['type'] = quest[0].text
            info['question'] = quest[1].text
            for q in quest[2:]:
                match = re.match(ur'[\u3000|\xa0|\s]+([A-Z]+)[\u3001](.+)$', q.text)
                if match:
                    info['options'][match.groups()[0]] = match.groups()[1]
                    continue
            for p in page.select('#message p'):
                if u"正确答案" in p.text:
                    info['answer'] = re.findall(r'[A-Za-z]', p.text)
                elif u"答案解析" in p.text:
                    info['reason'] = p.text
            
            info['date'] = info['date'].date()
            return Quest.objects.get_or_create(**info)
        except Exception, e:
            print e, link

class Parse(object):

    def __init__(self):
        self.link_list = []
        self.total = 0
        self.counter = 0
        self.br = mechanize.Browser()
        self.quest = []
        self.error = []


    def get_client(self):
        return redis.StrictRedis(db=0)

    def get_needed_links(self, br):
        for link in br.links(url_regex=r'^/zhucekuaijishi/mryl\S+.shtml$'):
            self.link_list.append(link)

    def follow_url(self, link=None):
        if not link:
            self.br.open(ROOT_URL)
            url = self.br.links(text="\xce\xb2\xd2\xb3").next().url
            self.total = int(re.match('page(\d+).shtm', url).groups()[0])
        else:
            self.br.follow_link(link)

        self.get_needed_links(self.br)
        next_page_link = list(self.br.links(text="\xcf\xc2\xd2\xbb\xd2\xb3"))
        if next_page_link:
            self.follow_url(next_page_link[0])

    def get_day_quests(self, link):
        #page = self.br.follow_link(link)
        url, absolute_url = link.url, link.absolute_url
        date_match = re.match(day_pattern, absolute_url).groups()[0]
        if client.exists(prefix + date_match):
            return
        print "new_quests", absolute_url
        self.br.open(absolute_url) 
        quests = []
        for l in self.br.links(url_regex=r"^.+zhucekuaijishi/mryl/\w\w%s\d+.shtml$"%(date_match)):
            if 'target' in dict(l.attrs) and re.match(day_pattern, l.absolute_url).groups()[0] == date_match:
                quests.append(l.absolute_url)
        if quests == []:
            print url
            return
        client.rpush(prefix+date_match, *quests)
        client.sadd("days_list", prefix + date_match)
        return

        #urls = page.select('#fontzoom span a')
        #for url in urls:
            #self.quest.append(self.get_quest_content(url))
            #print "success"
        #except URLError as e:
            #print link.absolute_url, e
            #self.error.append(link.absolute_url)
        #except socket.timeout as e:
            #self.error.append(link.absolute_url)
            #print link.absolute_url, e

    def get_quest_content(self, link, force=False):
        #link = "http://www.chinaacc.com/zhucekuaijishi/mryl/yu2014051308372597242889.shtml"
        #link = 'http://www.chinaacc.com/zhucekuaijishi/mryl/ya2014032909012963701628.shtml'
        #link = "http://www.chinaacc.com/zhucekuaijishi/mryl/sh2014051709225974031849.shtml"
        #link = "http://www.chinaacc.com/zhucekuaijishi/mryl/wa2014052008504669376405.shtml"
        #link = "http://www.chinaacc.com/zhucekuaijishi/mryl/zh2014060109140886125959.shtml"
        #http://www.chinaacc.com/zhucekuaijishi/mryl/ya2014051810115089335189.shtml
        md5 = hashlib.md5(link).hexdigest()
        date_match = re.match(day_pattern, link).groups()[0]
        date = datetime.datetime.strptime(date_match, date_fmt)
        if not force and client.exists("quest:" + md5):
            return 
        try:
            info = {'options': {}}
            info['link'] = link
            info['date'] = date
            info['uid'] = md5
            self.br.open(link)
            page = bs(self.br.response().read())
            info['title'] = page.select(".news_content h1")[0].text
            show_button = page.select('#fontzoom p input[type=button]')[0]
            quest = show_button.parent.find_previous_siblings('p')
            quest.reverse()
            for q in quest:
                if q.select('script'):
                    quest.remove(q)
            info['type'] = quest[0].text
            info['question'] = quest[1].text
            for q in quest[2:]:
                match = re.match(ur'[\u3000|\xa0|\s]+([A-Z]+)[\u3001](.+)$', q.text)
                if match:
                    info['options'][match.groups()[0]] = match.groups()[1]
                    continue
            for p in page.select('#message p'):
                if u"正确答案" in p.text:
                    info['answer'] = re.findall(r'[A-Za-z]', p.text)
                elif u"答案解析" in p.text:
                    info['reason'] = p.text
            client.set("quest:"+md5, pickle.dumps(info))
            client.sadd("quest_list", "quest:" + md5)
            return info
        except Exception, e:
            print e, link

    def clean_all(self):
        self.client

    def sorted_day_list(self):
        pass

    def run(self):
        client.flushdb()
        self.follow_url()
        for index, link in enumerate(self.link_list):
            self.get_day_quests(link)
        print client.scard('days_list')
        #self.get_quest_content(None)
        #client.delete(*client.keys('quest:*'))
        #count = 0
        for key in client.smembers('days_list'):
            urls = client.lrange(key, 0, 20)
            for url in urls:
                self.get_quest_content(url, force=False)
        print client.scard('quest_list')

    def patch(self):
        for key in client.keys('quest:*'):
            prefix, sufix = key.split(':')
            client.hset(key, 'uid', sufix)

    def add_missing_options(self):
        for key in client.keys('quest:*'):
            quest = client.hgetall(key)
            if not eval(quest["options"]):
                self.get_quest_content(quest['link'], force=True)

    def add_missing_answers(self):
        for key in client.keys('quest:*'):
            quest = client.hgetall(key)
            if 'reason' not in quest:
                continue
            if not quest['reason']:
                self.get_quest_content(quest['link'], force=True)

        #sleep(3)
        ##pool = Pool(processes=5)
        ##pool.map(self.get_day_quests, self.link_list)
        ##print len(self.link_list)
        #threads = [threading.Thread(target=self.get_day_quests, args=(link,)) for link in self.link_list]
        #while all([not thread.is_alive() for thread in threads]):
            #sleep(1)
        #threads = [threading.Thread(target=self.get_day_quests, args=(link,)) for link in self.link_list]
        #for thread in threads:
            #thread.start()
        #for thread in threads:
            #thread.join()
        #print len(self.quest)
        #for link in self.error:
            #print link
        # get answer
    def migrate(self):
        quests = client.keys('quest:*')
        print len(quests)
        from index.models import Quest
        for q in quests:
            info = pickle.loads(client.get(q))
            #info['date'] = datetime.datetime.strptime(date, "%Y-%m-%d 00:00:00").date()
            info['date'] = info['date'].date()
            try:
                Quest.objects.get_or_create(**info)
            except:
                print info
        


if __name__ == '__main__':
    p = Parse()
    #p.get_quest_content(None, force=True)
    #p.get_day_quests()
    #p.get_day_quests('http://www.chinaacc.com/zhucekuaijishi/mryl/zh2014060109244211866160.shtml')
    #p.add_missing_options()
    #p.add_missing_answers()

    #p.run()
    p.migrate()
    #p.patch()
    #p.get_quest_content(None)

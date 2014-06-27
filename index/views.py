# Create your views here.
from django.views.generic import TemplateView, FormView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.conf import settings

from urllib import urlopen
import redis
import json
from traceback import print_exc
from models import Quest, ErrorRecord
from parser import Updater
import datetime
RANK_GLOBAL = "global"
RANK_WEEK = "week"

RANK_LIST = "rank_info:user_list"

class CacheDB(object):
    client = None
    def connect(self):
        return self.get_client()
        #if not self.client:
            #self.get_client()
        #return self.client

    def get_client(self):
        try:
            self.client =  redis.Redis(**settings.REDIS_DB)
            return self.client
        except redis.ConnectionError:
            print_exc()
            pass
            


    def get_latest_quests(self):
        day = Quest.objects.all().latest('date').date
        return Quest.objects.filter(date=day)

        #days = sorted(map(lambda k: int(k.split(':')[1]), c.smembers('days_list')))
        #if days:
            #latest_day = days[-1]
        #else:
            #latest_day = {}
        #return self.get_quests_by_day(latest_day)

    def get_sorted_groups(self):
        return Quest.objects.all().values_list('date', flat=True).distinct()

        #c = self.connect()
        #return sorted(map(lambda k: int(k.split(':')[1]), c.smembers('days_list')), reverse=True)

    def get_quests_by_day(self, day):
        return Quest.objects.filter(date=day)

        #c = self.connect()
        #urls = c.lrange("parse:%s"%day, 0, 20)
        #quests = []
        #for u in urls:
            #quests.append(self.get_quest_by_link(u))
        #return quests

    #def get_quest_by_link(self, url):
        #if not len(url) == 32:
            #sufix = md5(url).hexdigest()
        #else:
            #sufix = url
        #c = self.connect()
        #quest = c.hgetall('quest:' + sufix)
        #print 'quest:%s'%sufix
        #if not quest:
            #return quest
        #option = quest['options']
        #answer = quest['answer']
        #quest['options'] = sorted(eval(option).items(), key=lambda k: k[0])
        #quest['answer'] = eval(answer)
        #return quest

    def add_error(self, user, quest):
        print user, quest
        ErrorRecord.objects.get_or_create(user=user, quest=quest)
        #c = self.connect()
        #c.sadd('error_set:%s'%pk, "quest:%s"%uid)

    def remove_error(self, user, quest):
        record = ErrorRecord.objects.get(user=user, quest=quest)
        record.passed = True
        record.save()
        #c = self.connect()
        #c.srem('error_set:%s'%pk, "quest:%s"%uid)

    def get_errors(self, user):
        records = ErrorRecord.objects.filter(user=user, passed=False)
        return map(lambda r: r.quest, records)
        #c = self.connect()
        #return map(lambda k: self.get_quest_by_key(k), c.smembers('error_set:%s'%pk))

    #def get_quest_by_key(self, key):
        #c = self.connect()
        #quest = c.hgetall(key)
        #option = quest['options']
        #answer = quest['answer']
        #quest['options'] = sorted(eval(option).items(), key=lambda k: k[0])
        #quest['answer'] = eval(answer)
        #return quest

    #def clear_this_day(self, day):
        #c = self.connect()
        #c.sadd('clear_day'

            
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
        day = datetime.datetime.strptime(uid, "%Y_%m_%d").date()
        rdb = CacheDB()
        kwargs['quests'] = rdb.get_quests_by_day(day)
        alls = rdb.get_sorted_groups()
        length = len(alls)
        index = list(alls).index(day)
        if index < 5:
            others = alls[:10]
        elif index > length -5:
            others = alls[-11:-1]
        else:
            others = alls[index-5:index+5]
        kwargs['others'] = others
        kwargs['day'] = day
        return super(QuestView, self).get_context_data(**kwargs)
    
class SignUpView(FormView):
    template_name = 'signup.html'
    form_class = UserCreationForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.success_url)

class ErrorView(TemplateView):
    template_name = 'quest.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        if not user.is_authenticated():
            return super(ErrorView, self).get_context_data(**kwargs)

        rdb = CacheDB()
        kwargs['quests'] = rdb.get_errors(user)
        return super(ErrorView, self).get_context_data(**kwargs)

class CompleteMeView(FormView):
    template_name = ""
    
    def get_context_data():
        pass

class LoginView(FormView):
    template_name = 'login.html'
    form_class = AuthenticationForm
    success_url = "/"

    def form_valid(self, form):
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        print form.errors
        return self.render_to_response(self.get_context_data(form=form))


def user_logout(request):
    logout(request)
    return redirect("/")

class JSONResponse(HttpResponse):

    def __init__(self, **kwargs):
        content = json.dumps(kwargs)
        super(JSONResponse, self).__init__(content, content_type='application/json')

def mark_failed(request):
    if request.user.is_authenticated():
        quest_uid = request.POST.get('uid', '')
        passed = request.POST.get('passed', '')
        if quest_uid:
            quest = Quest.objects.get(pk=quest_uid)
            rdb = CacheDB()
            if passed == 'true':
                rdb.remove_error(request.user, quest)
            elif passed == 'false':
                rdb.add_error(request.user, quest)
            return JSONResponse(success=True)
    return JSONResponse(success=False)

def mark_day_cleared(request):
    if request.user.is_authenticated():
        day = request.POST.get('day', '')
        if day:
            rdb = CacheDB()
            rdb.sadd('clean_day:%s'%request.user.pk, "parse:%s"%day)
            return JSONResponse(success=True)
    return JSONResponse(success=False)

def update_quests(request):
    today = datetime.date.today()
    if Quest.objects.filter(date=today).exists():
        return JSONResponse(success=False, text='already update')

    start_date = Quest.objects.latest('date').date
    while start_date <= today:
        try:
            u = Updater()
            u.get_today_quests(start_date)
        except Exception, e:
            continue
        start_date += datetime.timedelta(days=1)
    return JSONResponse(success=True)

def get_single_quest(request):
    url = request.GET.get('url', '')
    try:
        urlopen(url)
        u = Updater()
        if u.get_quest_content(url):
            return JSONResponse(success=True)
        else:
            return JSONResponse(success=False)
    except IOError:
        return JSONResponse(success=False)
    

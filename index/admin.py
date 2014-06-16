from django.contrib import admin
from index.models import Quest
from django import forms

try:
	import cPickle as pickle
except ImportError:
	import pickle

class QuestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestForm, self).__init__(*args, **kwargs)
        self.initial['options'] = pickle.loads(str(self.instance.options))
        self.initial['answer'] = pickle.loads(str(self.instance.answer))

    class Meta:
        model = Quest

class QuestAdmin(admin.ModelAdmin):
    form = QuestForm

admin.site.register(Quest, QuestAdmin)

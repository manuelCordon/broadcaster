import os
import sys
import views
from im.core.config import configure
from django.conf.urls import patterns, include, url

sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))
configure(set_project_path=os.path.dirname(os.path.abspath(__file__)) + '/', override='PARTIAL')

urlpatterns = patterns('',
    url(r"^$", views.index, name="index"),
    #campaign handling
    url(r"^campaign/new$", views.campaign, name="campaign"),
    url(r"^campaign/save$", views.campaign_save, name="save campaign"),
    url(r"^campaign/upload$", views.upload_file, name="actual upload"),
    url(r"^campaign/edit/(?P<_id>\w+)$", views.campaign_edit, name="edit campaign"),
    url(r"^campaign/remove/(?P<_id>\w+)$", views.campaign_remove, name="remove campaign"),
    url(r"^campaign/list$", views.campaign_list, name="list of campaigns"),
    #scheduler
    url(r"^scheduler/daily$", views.scheduler_daily, name="daily schedule")
)
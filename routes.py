import os
import sys
import views
import controllers.scheduler
from im.core.config import configure
from django.conf.urls import patterns, url

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
    #lists management
    url(r"^blacklist$", controllers.listmanagement.show_blacklist, name="black list management"),
    url(r"^whitelist$", controllers.listmanagement.show_whitelist, name="white list management"),
    #scheduler
    url(r"^scheduler/daily$", controllers.scheduler.daily_no_day, name="daily schedule"),
    url(r"^scheduler/daily/(?P<day>(\d+){4}[-](\d+){2}[-](\d+){2})$", controllers.scheduler.daily, name="daily schedule"),
    url(r"^scheduler/save/(?P<day>(\d+){4}[-](\d+){2}[-](\d+){2})$", controllers.scheduler.daily_save, name="daily schedule save"),
    #reports
    url(r"^reports/progress$", controllers.progressreport.no_day, name="progress report with no date"),
    url(r"^reports/progress/(?P<day>(\d+){4}[-](\d+){2}[-](\d+){2})$", controllers.progressreport.day, name="progress report"),
)
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
    url(r"^campaign/new$", controllers.campaigns.edit, name="campaign"),
    url(r"^campaign/save$", controllers.campaigns.save, name="save campaign"),
    url(r"^campaign/upload$", controllers.campaigns.upload, name="actual upload"),
    url(r"^campaign/edit/(?P<_id>(\w+){24})$", controllers.campaigns.edit, name="edit campaign"),
    url(r"^campaign/remove/(?P<_id>(\w+){24})$", controllers.campaigns.remove, name="remove campaign"),
    url(r"^campaign/discard$", controllers.campaigns.remove, name="discard empty campaigns"),
    url(r"^campaign/list$", controllers.campaigns.show, name="list of campaigns"),
    #lists management
    url(r"^lists/upload", controllers.listsmanagement.upload_file, name="upload document"),
    url(r"^lists/(?P<type>(\w+){5})$", controllers.listsmanagement.show, name="list management"),
    url(r"^lists/(?P<type>(\w+){5})/new$", controllers.listsmanagement.edit, name="new list"),
    url(r"^lists/(?P<type>(\w+){5})/save$", controllers.listsmanagement.save, name="discard empty lists"),
    url(r"^lists/(?P<type>(\w+){5})/discard$", controllers.listsmanagement.discard, name="discard empty lists"),
    url(r"^lists/(?P<type>(\w+){5})/edit/(?P<_id>(\w+){24})$", controllers.listsmanagement.edit, name="edit list"),
    url(r"^lists/(?P<type>(\w+){5})/remove/(?P<_id>(\w+){24})$", controllers.listsmanagement.remove, name="remove list"),
    #scheduler
    url(r"^scheduler/daily$", controllers.scheduler.daily_no_day, name="daily schedule"),
    url(r"^scheduler/daily/(?P<day>(\d+){4}[-](\d+){2}[-](\d+){2})$", controllers.scheduler.daily, name="daily schedule"),
    url(r"^scheduler/save/(?P<day>(\d+){4}[-](\d+){2}[-](\d+){2})$", controllers.scheduler.daily_save, name="daily schedule save"),
    #reports
    url(r"^reports/progress$", controllers.progressreport.no_day, name="progress report with no date"),
    url(r"^reports/progress/(?P<day>(\d+){4}[-](\d+){2}[-](\d+){2})$", controllers.progressreport.day, name="progress report"),
)
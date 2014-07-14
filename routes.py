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
    # Session handling
    url(r'login/$', 'django.contrib.auth.views.login', name="login"),
    url(r'logout/$', 'django.contrib.auth.views.logout', name='logout'),
    # User handling
    url(r'^user/list$', controllers.users.show, name="List of users"),
    url(r"^user/new$", controllers.users.edit, name="new user"),
    url(r"^user/edit/(?P<_id>(\d+)+)$", controllers.users.edit, name="edit user"),
    url(r"^user/save$", controllers.users.save, name="save user"),
    # Campaign handling
    url(r"^campaign/new$", controllers.campaigns.edit, name="campaign"),
    url(r"^campaign/save$", controllers.campaigns.save, name="save campaign"),
    url(r"^campaign/upload$", controllers.campaigns.upload, name="actual upload"),
    url(r"^campaign/edit/(?P<_id>(\w+){24})$", controllers.campaigns.edit, name="edit campaign"),
    url(r"^campaign/remove/(?P<_id>(\w+){24})$", controllers.campaigns.remove, name="remove campaign"),
    url(r"^campaign/discard$", controllers.campaigns.discard, name="discard empty campaigns"),
    url(r"^campaign/list$", controllers.campaigns.show, name="list of campaigns"),
    url(r"^campaign/pause/(?P<_id>(\w+){24})$", controllers.campaigns.pause, name="Pauses a campaign"),
    url(r"^campaign/resume/(?P<_id>(\w+){24})$", controllers.campaigns.resume, name="Resumes a campaign"),
    # Campaign authorizations
    url(r"^authorization/list$", controllers.authorizations.show, name="list of campaigns"),
    url(r"^authorization/(P<status>(w+)+)/(?P<_id>(\w+){24})$", controllers.authorizations.set_authorization, name="list of campaigns"),
    # Lists management
    url(r"^lists/upload", controllers.listsmanagement.upload_file, name="upload document"),
    url(r"^lists/(?P<list_type>(\w+){5})$", controllers.listsmanagement.show, name="list management"),
    url(r"^lists/(?P<list_type>(\w+){5})/json", controllers.listsmanagement.json_items, name="reply the content of the lists"),
    url(r"^lists/(?P<list_type>(\w+){5})/new$", controllers.listsmanagement.edit, name="new list"),
    url(r"^lists/(?P<list_type>(\w+){5})/save$", controllers.listsmanagement.save, name="discard empty lists"),
    url(r"^lists/(?P<list_type>(\w+){5})/discard$", controllers.listsmanagement.discard, name="discard empty lists"),
    url(r"^lists/(?P<list_type>(\w+){5})/edit/(?P<_id>(\w+){24})$", controllers.listsmanagement.edit, name="edit list"),
    url(r"^lists/(?P<list_type>(\w+){5})/remove/(?P<_id>(\w+){24})$", controllers.listsmanagement.remove, name="remove list"),
    # Scheduler
    url(r"^scheduler/daily$", controllers.scheduler.daily_no_day, name="daily schedule"),
    url(r"^scheduler/daily/(?P<day>(\d+){4}[-](\d+){2}[-](\d+){2})$", controllers.scheduler.daily, name="daily schedule"),
    url(r"^scheduler/save/(?P<day>(\d+){4}[-](\d+){2}[-](\d+){2})$", controllers.scheduler.daily_save, name="daily schedule save"),
    # Reports
    url(r"^reports/progress$", controllers.progressreport.no_day, name="progress report with no date"),
    url(r"^reports/progress/(?P<day>(\d+){4}[-](\d+){2}[-](\d+){2})$", controllers.progressreport.day, name="progress report"),
)
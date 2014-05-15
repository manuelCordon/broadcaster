import locale
from bson import ObjectId
import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from im.core.config import conf
import time
from Forms import *
import logging

__author__ = 'manuel'

# Shows the list of the black lists available in the system.
def show_blacklist(request):
    return show_list(request, "black")

# Shows the list of the white lists available in the system.
def show_whitelist(request):
    return show_list(request, "white")

# Shows the list based on the type specified.
def show_list(request, type):

    # Get the lists by type from the database.
    lists = tuple(ConfigDB().get_collection("lists", {"type": type}))

    # Replace _id to list_id to be consumed by the template since no _ starting ids can be used.
    for l in lists:
        l["list_id"] = c.pop("_id")

    return render(request, "lists/list.html", {"lists": lists, "title": "Listas negras"})
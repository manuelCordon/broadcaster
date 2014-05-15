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

from django import template
register = template.Library()
watch_folder = conf("config.watch_folder")

@register.simple_tag
def dict_key_lookup(the_dict, key):
    return the_dict.get(key, '')


def index(request):
    return render(request, "hello.html", dict(test="xxyy"))


def campaign(request):
    return render(request, 'campaign/edit.html', dict(form=CampaignForm),)


@csrf_exempt
def campaign_save(request):
    if request.method == "POST":
        cdb = ConfigDB()
        f = request.POST

        # Try to retrieve campaign from db, if not possible generate an empty campaign.
        try:
            id = ObjectId(str(f["campaign_id"]))
            c = ConfigDB().get_document("campaigns", {"_id": id})
        except:
            id = None
            c = {}

        # Keep the last status, if no status found will be set as missing data file.
        c["status"] = c.get("status", "missing data file")

        # Update the rest of the campaign data.
        c["message"] = f.get("message", "NO MESSAGE")
        c["name"] = f.get("name")
        c["destination"] = f.get("destination", None)
        c["start_date"] = f.get("start_date", None)
        c["end_date"] = f.get("end_date", None)
        c["ignore_max_sms_policy"] = f.get("ignore_max_sms_policy", None)
        c["blacklist"] = f.get("blacklists", None)
        c["whitelist"] = f.get("whitelists", None)

        destination_id = f.get("destination", None)
        if destination_id is not None:
            c["destination"] = destination_id

        priority_id = f.get("priority", None)
        if priority_id is not None:
            c["priority"] = ObjectId(priority_id)
            priority = cdb.get_document("priorities", {"_id": c["priority"]})
            c["priority_factor"] = priority["factor"]

        owner_id = f.get("owner", None)
        if owner_id is not None:
            c["owner"] = ObjectId(owner_id)
            owner = cdb.get_document("users", {"profile": "owner", "_id": ObjectId(owner_id)})

        category_id = f.get("category", None)
        if category_id is not None:
             c["category"] = ObjectId(category_id)
             category = cdb.get_document("categories", {"_id": ObjectId(category_id)})

        product_id = f.get("product", None)
        if product_id is not None:
            c["product"] = ObjectId(product_id)
            product = cdb.get_document("products", {"_id": ObjectId(product_id)})

        ConfigDB().set_document(
            collection="campaigns",
            _id=id,
            values=c
        )

        return HttpResponseRedirect("/campaign/list", {"msg":"save_ok"})


def campaign_remove(request, _id):
    ConfigDB().dispose_document("campaigns", {"_id": ObjectId(_id)})
    return HttpResponseRedirect("/campaign/list", {"msg":"delete_ok"})


def campaign_edit(request, _id):
    c = ConfigDB().get_collection("campaigns", {"_id": ObjectId(_id)})[0]
    c["campaign_id"] = c.pop("_id")
    frm = CampaignForm(initial=c)
    return render(request, "campaign/edit.html", {"form": frm})


def campaign_list(request):
    # Get the message if any.
    if request.method == "POST":
        msg = request.POST.get("msg", None)
    else:
        msg = None

    # Get the campaigns from the database.
    campaigns = tuple(ConfigDB().get_collection("campaigns"))

    # Replace _id to campaign_id to be consumed by the template since no _ starting ids can be used.
    for c in campaigns:
        c["campaign_id"] = c.pop("_id")
    return render(request, "campaign/list.html", {"campaigns": campaigns, "message": msg})


@csrf_exempt
def upload_file(request):
    if request.method == 'POST':

        # Get campaign id if available.
        logging.info("Received post to upload file for {0}".format(request.POST.get("campaign_id", "")))
        camp_id = request.POST.get("campaign_id", "")
        if camp_id != "":
            camp_id = ObjectId(camp_id)
        else:
            camp_id = None

        # Insert/Update campaign with upload date.
        logging.info("Adding upload date.")
        c = ConfigDB().set_document("campaigns",
                                    camp_id,
                                    {"data_date": datetime.datetime.now().isoformat(),
                                     "status": "uploading data file"})

        # Make sure campaign id is assigned.
        camp_id = str(c.get("_id", None))
        logging.info("Confirmed campaign id ".format(camp_id))

        # Write the file in the server.
        save_file(request.FILES['fileToUpload'], camp_id)

        # Set camapign status ready for watcher.
        ConfigDB().set_document("campaigns",
                                camp_id,
                                {"status": "ready for watcher"})

        # Return the campaign id to be assigned.
        return render(request, "blank.html", {"message": camp_id})


def save_file(f, name):
    filename = watch_folder + "camp_" + name + ".zip"
    with open(filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    logging.info("File saved in watch folder {0}.".format(filename))
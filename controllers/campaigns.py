import datetime
import logging

from bson import ObjectId
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from im.core.config import conf
from django import template

from Forms import *


register = template.Library()
watch_folder = conf("config.watch_folder")
__author__ = 'manuel'


def show(request):
    # Get the message if any.
    if request.method == "GET":
        msg = request.GET.get("msg", None)
    else:
        msg = None

    # Get the campaigns from the database.
    campaigns = tuple(ConfigDB().get_collection("campaigns"))

    # Replace _id to campaign_id to be consumed by the template since no _ starting ids can be used.
    for c in campaigns:
        c["campaign_id"] = c.pop("_id")

    return render(request, "campaign/list.html", {"campaigns": campaigns, "message": msg})


# Allows add/edit campaigns.
def edit(request, _id=None):
    if _id is None:
        # No _id, generates an empty campaign.
        c = ConfigDB().set_document("campaigns", None, {})
    else:
        # Reads the list from the db.
        c = ConfigDB().get_document("campaigns", {"_id": ObjectId(_id)})

    # Replaces _id with campaign_id.
    c["campaign_id"] = c.pop("_id")

    # Preload the form to be submitted.
    frm = CampaignForm(initial=c)

    return render(request, "campaign/edit.html", {"form": frm})


# Removes the campaign from the system.
def remove(request, _id):
    ConfigDB().dispose_document("campaigns", {"_id": ObjectId(_id)})
    return HttpResponseRedirect("/campaign/list?msg=delete_ok")


# Removes the campaigns without status empty from the system silently.
def discard(request):
    ConfigDB().dispose_document("lists",
                                {"status": {"$exists": False}})
    return HttpResponseRedirect("/campaign/list")


# Save the campaign in the db.
@csrf_exempt
def save(request):
    # If not POST do nothing.
    if request.method == "POST":
        cdb = ConfigDB()
        f = request.POST

        # Try to retrieve campaign from db, if not possible generate an empty campaign.
        _id = ObjectId(str(f["campaign_id"]))
        c = ConfigDB().get_document("campaigns", {"_id": _id})


        # Update the rest of the campaign data.
        c["message"] = f.get("message", "NO MESSAGE")
        c["name"] = f.get("name")
        c["destination"] = f.get("destination", None)
        c["start_date"] = f.get("start_date", None)
        c["end_date"] = f.get("end_date", None)
        c["ignore_max_sms_policy"] = f.get("ignore_max_sms_policy", None)

        # Convert list of black lists from strings to ObjectIDs.
        lst = []
        for l in f.getlist("blacklists"):
            lst += [ObjectId(l)]
        list_changed = lst != c["blacklists"]
        c["blacklists"] = lst

        # Convert list of white lists from strings to ObjectIDs.
        lst = []
        for l in f.getlist("whitelists"):
            lst += [ObjectId(l)]
        c["whitelists"] = lst
        list_changed = list_changed and (lst != c["whitelists"])

        # Handle destination change.
        destination_id = f.get("destination", None)
        if destination_id is not None:
            c["destination"] = destination_id

        # Save priority and priority factor.
        priority_id = f.get("priority", None)
        if priority_id is not None:
            c["priority"] = ObjectId(priority_id)
            priority = cdb.get_document("priorities", {"_id": c["priority"]})
            c["priority_factor"] = priority["factor"]

        # Extract campaign owner.
        owner_id = f.get("owner", None)
        if owner_id is not None:
            c["owner"] = ObjectId(owner_id)
            owner = cdb.get_document("users", {"profile": "owner", "_id": ObjectId(owner_id)})

        # Extract product category.
        category_id = f.get("category", None)
        if category_id is not None:
             c["category"] = ObjectId(category_id)
             category = cdb.get_document("categories", {"_id": ObjectId(category_id)})

        # Extract product id.
        product_id = f.get("product", None)
        if product_id is not None:
            c["product"] = ObjectId(product_id)
            product = cdb.get_document("products", {"_id": ObjectId(product_id)})

        # Keep the last status, if no status found will be set as missing data file.
        status = c.get("status", "missing data file")
        if list_changed and status not in ["missing data file", "ready for watcher", "ready for bw list import"]:
            c["status"] = "ready for bw list import"
        else:
            c["status"] = status

        # Update the campaign document.
        ConfigDB().set_document(
            collection="campaigns",
            _id=_id,
            values=c
        )

        return HttpResponseRedirect("/campaign/list?msg=save_ok")


@csrf_exempt
def upload(request):
    if request.method == 'POST':

        # Get campaign id if available.
        logging.info("Received post to upload file for {0}".format(request.POST.get("campaign_id", "")))
        camp_id = ObjectId(request.POST.get("campaign_id"))

        # Update campaign with upload date.
        logging.info("Adding upload date.")
        c = ConfigDB().set_document("campaigns",
                                    camp_id,
                                    {"data_date": datetime.datetime.now().isoformat(),
                                     "status": "uploading data file"})

        # Write the file in the server.
        save_file(request.FILES['fileToUpload'], camp_id)

        # Set camapign status ready for watcher.
        ConfigDB().set_document("campaigns",
                                camp_id,
                                {"status": "ready for watcher"})

        # Return the campaign id to be assigned.
        return render(request, "blank.html", {"message": "OK"})


def save_file(f, _id):
    filename = "{0}camp_{1}.zip".format(watch_folder, _id)
    with open(filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    logging.info("File saved in watch folder {0}.".format(filename))
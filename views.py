from bson import ObjectId
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import time
from Forms import *

from django import template
register = template.Library()


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
        f = request.POST
        try:
            id = ObjectId(str(f["campaign_id"]))
            c = ConfigDB().get_document("campaigns", {"_id": id})
        except:
            id = None
            c = {}
        c["status"] = "ready for watcher"
        c["name"] = f.get("name")
        c["start_date"] = f.get("start_date", None)
        c["destenation"] = f.get("destenation", None)
        c["start_date"] = f.get("start_date", None)
        c["end_date"] = f.get("end_date", None)
        c["priority"] = f.get("priority", None)
        c["ignore_max_sms_policy"] = f.get("ignore_max_sms_policy", None)
        c["blacklist"] = f.get("blacklists", None)
        c["whitelist"] = f.get("whitelists", None)

        owner_id = f.get("owner", None)
        if owner_id is not None:
            c["owner"] = ConfigDB().get_document("users", {"profile": "owner", "_id": ObjectId(owner_id)})

        category_id = f.get("category", None)
        if category_id is not None:
            c["category"] = ConfigDB().get_document("categories", {"_id": ObjectId(category_id)})

        product_id = f.get("product", None)
        if product_id is not None:
            c["product"] = ConfigDB().get_document("products", {"_id": ObjectId(product_id)})

        ConfigDB().set_campaign(
            _id=id,
            values=c
        )
        return HttpResponseRedirect("/campaign/list?msg=save_ok")


def campaign_remove(request, _id):
    return render(request, "campaign/remove.html")


def campaign_edit(request, _id):
    c = ConfigDB().get_collection("campaigns", {"_id": ObjectId(_id)})[0]
    c["campaign_id"] = c.pop("_id")
    frm = CampaignForm(initial=c)
    return render(request, "campaign/edit.html", {"form": frm})


def campaign_list(request):
    if request.method == "GET":
        msg = request.GET.get("msg", None)

    campaigns = tuple(ConfigDB().get_collection("campaigns"))
    for c in campaigns:
        c["campaign_id"] = c.pop("_id")
    return render(request, "campaign/list.html", {"campaigns": campaigns, "message": msg})


@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        c = ConfigDB().set_campaign(None, {"status": "empty", "date": time.strftime("%c")})
        id = str(c["_id"])
        save_file(request.FILES['fileToUpload'], id)
        return render(request, "blank.html",  dict(message=id))


def save_file(f, name):
    with open("/home/manuel/camp_" + name + ".zip", 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def scheduler_daily(request):
    campaigns = tuple(ConfigDB().get_collection("campaigns"))
    for c in campaigns:
        c["campaign_id"] = c.pop("_id")
    return render(request, "scheduler/daily.html", {"campaigns": campaigns})
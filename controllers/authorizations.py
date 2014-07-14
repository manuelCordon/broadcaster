from bson import ObjectId
import datetime
from django.shortcuts import render
from data import ConfigDB

__author__ = 'manuel'


# Show pending authorizations.
def show(request):
    # Check for the specific permission.
    if not request.user.has_perm("broadcaster.campaign_authorize"):
        return render(request, "access_denied.html")

    # Get message if any.
    if request.method == "GET":
        msg = request.GET["msg"]
    else:
        msg = ""

    # Fetch campaigns.
    campaigns = ConfigDB().get_collection("campaigns",
                                          {"owner": request.user.username,
                                           "authorization_date": {"$exists": False}})

    return render(request, "campaign/authorize.html", {"campaigns": campaigns, "message": msg})


# Approve or revoke the campaign.
def set_authorization(request, status, _id):
    # Check for the specific permission.
    if not request.user.has_perm("broadcaster.campaign_authorize"):
        return render(request, "access_denied.html")

    cdb = ConfigDB()
    _id = ObjectId(_id)
    authorized = status.lower() == "approve"

    # Get campaign to see if status must be updated.
    camp = cdb.get_document("campaign", {"_id": _id})
    status = "ready to broadcast" if authorized and camp["status"] == "waiting for owner's authorization" \
        else camp["status"]

    # Update the document.
    cdb.set_document(collection="campaigns",
                            _id=_id,
                            values={"status": status,
                                    "authorized": authorized,
                                    "authorization_date": datetime.datetime.now().isoformat()})

    return HttpResponseRedirect("/authorizations/list")
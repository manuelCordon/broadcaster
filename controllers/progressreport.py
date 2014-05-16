import datetime

from bson import ObjectId
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from im.core.config import conf
import logging

import json

from dataAccess import ConfigDB, DataDB

__author__ = 'manuel'

# If no day, redirect to today's report.
def no_day(request):
    day = datetime.date.today().isoformat()[0:10]
    return HttpResponseRedirect("/reports/progress/" + day)

# Returns the basic template for the ongoing campaigns.
def day(request, day):

    # Init the config db.
    cdb = ConfigDB()

    # Get the prev_day, next_day and hour variables.
    hour = datetime.datetime.now().isoformat()[11:26]
    prev_day = (datetime.datetime.strptime(day, "%Y-%m-%d") - datetime.timedelta(days=1)).isoformat()[0:10]
    next_day = (datetime.datetime.strptime(day, "%Y-%m-%d") + datetime.timedelta(days=1)).isoformat()[0:10]

    # Get the list of the campaigns in progress.
    schedule = ConfigDB().get_collection("schedules", where={"day":day})
    campaigns = []
    for camp_schedule in schedule:

        # Init campaign in and out.
        campaign = cdb.get_document("campaigns", {"_id": camp_schedule["campaign_id"]})
        ddb = DataDB(str(camp_schedule["campaign_id"]))
        campaign_out = {}

        # Get campaign name and status.
        campaign_out["name"] = campaign["name"]
        campaign_out["status"] = campaign["status"]
        volume = campaign["volume"]
        campaign_out["queue_count"] = ddb.count_documents("data", {"status": {"$exists": False}})
        campaign_out["noresponse_count"] = ddb.count_documents("data", {"status": "sent"})
        campaign_out["success_count"] = ddb.count_documents("data", {"status": 0})
        campaign_out["throttling_count"] = ddb.count_documents("data", {"status": 88})

        # Append campaign.
        campaigns += [campaign_out]

    # Read the data from tps_history.
    range_start = day + " 00:00:00"
    range_end = day + " 23:59:59"
    logging.info("Seek history between {0} and {1}".format(range_start, range_end))
    logCur = cdb.get_collection("tps_history",
                                {"_id": {"$gt": range_start, "$lt": range_end}})

    data = [0] * 24 * 3600
    for log in logCur:
        t = datetime.datetime.strptime(log["_id"], "%Y-%m-%d %H:%M:%S")
        index = t.hour * 3600 + t.minute * 60 + t.second
        logging.info("update {0} con {1}".format(index, log["tps"]))
        data[index] = log["tps"]

    return render(request,
                  "reports/progress.html",
                  {"year_num": day[0:4],
                   "month_num": int(day[5:7]) - 1,
                   "day_num": day[8:10],
                   "day": day,
                   "hour": hour,
                   "next_day": next_day,
                   "prev_day": prev_day,
                   "campaigns": campaigns,
                   "data": json.dumps(data)
                   })

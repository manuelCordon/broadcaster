import datetime
import logging
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from data.mongo_data_access import ConfigDB, DataDB

__author__ = 'manuel'


# If no day, redirect to today's report.
@login_required
def no_day(request):
    # Check for the specific permission.
    if not request.user.has_perm("broadcaster.reports_view"):
        return render(request, "access_denied.html")

    day = datetime.date.today().isoformat()[0:10]
    return HttpResponseRedirect("/reports/progress/" + day)


# Returns the basic template for the ongoing campaigns.
@login_required
def day(request, day):
    # Check for the specific permission.
    if not request.user.has_perm("broadcaster.reports_view"):
        return render(request, "access_denied.html")

    # Init the config db.
    cdb = ConfigDB()

    # Get the prev_day, next_day and hour variables.
    hour = datetime.datetime.now().isoformat()[11:26]
    prev_day = (datetime.datetime.strptime(day, "%Y-%m-%d") - datetime.timedelta(days=1)).isoformat()[0:10]
    next_day = (datetime.datetime.strptime(day, "%Y-%m-%d") + datetime.timedelta(days=1)).isoformat()[0:10]

    # Get the list of the campaigns in progress.
    schedule = ConfigDB().get_collection("schedules", where={"day": day})
    campaigns = []
    for camp_schedule in schedule:
        # Init campaign in and out.
        campaign = cdb.get_document("campaigns", {"_id": camp_schedule["campaign_id"]})
        ddb = DataDB(str(camp_schedule["campaign_id"]))
        campaign_out = {}

        # Get campaign name and status.
        campaign_out["campaign_id"] = campaign["_id"]
        campaign_out["name"] = campaign["name"]
        campaign_out["status"] = campaign["status"]
        campaign_out["queue_count"] = ddb.count_documents("data", {"status": {"$exists": False}})
        campaign_out["noresponse_count"] = ddb.count_documents("data", {"status": "sent"})
        campaign_out["success_count"] = ddb.count_documents("data", {"status": 0})
        campaign_out["throttling_count"] = ddb.count_documents("data", {"status": 88})
        campaign_out["response_to_count"] = ddb.count_documents("data", {"status": "response time out"})

        # Append campaign.
        campaigns += [campaign_out]

    # Read the data from tps_history.
    range_start = day + " 00:00:00"
    range_end = day + " 23:59:59"
    logging.info("Seek history between {0} and {1}".format(range_start, range_end))
    logCur = cdb.get_collection("tps_history",
                                {"_id": {"$gt": range_start, "$lt": range_end}})

    tps_data = [0] * 24 * 3600
    throttling_data = [0] * 24 * 3600

    logging.info("Building data.")

    for log in logCur:
        t = datetime.datetime.strptime(log["_id"], "%Y-%m-%d %H:%M:%S")
        index = t.hour * 3600 + t.minute * 60 + t.second
        tps_data[index] = log["tps"]
        try:
            throttling_data[index] = log["throting"]
        except KeyError:
            throttling_data[index] = 0

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
                   "tps_data": json.dumps(tps_data),
                   "throttling_data": json.dumps(throttling_data),
                  })

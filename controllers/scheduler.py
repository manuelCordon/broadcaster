import datetime

from bson import ObjectId
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from im.core.config import conf

from data.mongo_data_access import ConfigDB


__author__ = 'manuel'

max_tps = conf("config.max_tps")


# Redirects to today's scheduler.
@login_required
def daily_no_day(request):
    # Check for the specific permission.
    if not request.user.has_perm("broadcaster.schedule_view"):
        return render(request, "access_denied.html")

    day = datetime.date.today().isoformat()[0:10]
    return HttpResponseRedirect("/scheduler/daily/" + day)


# Returns the list of tps pre assigned to accomplish the transactions within the time range.
@login_required
def daily(request, day):
    # Check for the specific permission.
    if not request.user.has_perm("broadcaster.schedule_view"):
        return render(request, "access_denied.html")

    cdb = ConfigDB()

    # Get the requested date.
    if day is None:
        day = datetime.datetime.today().isoformat()[0:10]

    # Get fixed hours if the day is today.
    if datetime.datetime.today().isoformat()[0:10] == day:
        hour = datetime.datetime.today().hour
    else:
        hour = 0

    # Get prev and next day.
    prev_day = (datetime.datetime.strptime(day, "%Y-%m-%d") - datetime.timedelta(days=1)).isoformat()[0:10]
    next_day = (datetime.datetime.strptime(day, "%Y-%m-%d") + datetime.timedelta(days=1)).isoformat()[0:10]

    # Build the list of schedules.
    schedule_db = cdb.get_collection(collection="schedules", where={"day": day})
    schedule = []
    scheduled_campaign_ids = []
    for s in schedule_db:
        schedule += [s]
        scheduled_campaign_ids += [s["campaign_id"]]

    # Fetch the missing campaigns.
    campaigns = cdb.get_collection(
        collection="campaigns",
        where={"status": {"$in": ["ready for scheduler", "broadcasting"]},
               "start_date": {"$lte": day},
               "end_date": {"$gte": day},
               "_id": {"$nin": scheduled_campaign_ids}})

    # If not found in db, create it.
    if campaigns.count() > 0:

        # Init variables.
        priority_sum = 0
        index_offset = len(schedule)

        # Append to the schedule the missing campaigns.
        for campaign in campaigns:
            priority_sum += campaign["priority_factor"]
            hours = []
            for hour in range(8, 20):
                hours += [{"hour": hour,
                           "tps": (campaign["priority_factor"] if index_offset == 0 else 0)}]
            schedule += [{"campaign": campaign["name"],
                          "campaign_id": campaign["_id"],
                          "volume": campaign["volume"],
                          "date": day,
                          "hours": hours}]

        # Apply formula and round tps.
        for s in schedule[index_offset:len(schedule)]:
            for h in s["hours"]:
                h["tps"] = int(h["tps"] * max_tps / priority_sum)

    return render(request, "scheduler/daily.html",
                  {"day": day,
                   "hour": hour,
                   "schedule": schedule,
                   "prev_day": prev_day,
                   "next_day": next_day
                  })


# Save the schedule grid and show it with a confirmation message.
# If errors found, the data is not saved and an error message is displayed.
@csrf_exempt
@login_required
def daily_save(request, day):
    # Check for the specific permission.
    if not request.user.has_perm("broadcaster.schedule_edit"):
        return render(request, "access_denied.html")

    if request.method == "POST":
        cdb = ConfigDB()
        f = request.POST
        daily_schedule = {}
        for key in sorted(f.keys()):

            # If is an hour textbox.
            if key.startswith("idh_"):

                # Get the information from each textbox.
                campaign_id = ObjectId(key[5:29])
                hour = int(key[31:33])
                if len(str(f[key]).strip()) == 0:
                    tps = 0
                else:
                    tps = int(f[key])

                if daily_schedule.has_key(campaign_id):
                    # If it does adds the hour entry.
                    daily_schedule[campaign_id]["hours"] += [{"hour": hour,
                                                              "tps": tps}]
                else:
                    # If the campaign doesn't exist creates it
                    campaign = cdb.get_document("campaigns", campaign_id)
                    daily_schedule.setdefault(campaign_id,
                                              {"campaign": campaign["name"],
                                               "volume": campaign["volume"],
                                               "campaign_id": campaign_id,
                                               "_id": day + "_" + str(campaign_id),
                                               "day": day,
                                               "hours": [{"hour": hour,
                                                          "tps": tps}]})

        # Insert schedules and build output.
        for key in daily_schedule.keys():
            cdb.set_document("schedules", daily_schedule[key]["_id"], daily_schedule[key])
            c = cdb.get_document("campaigns", {"_id": key})

            status = "ready to broadcast"
            if c["authorization_required"] and not "authorized" in c:
                status = "waiting for owner's authorization"
            elif c["authorization_required"] and not c["authorized"]:
                status = c["status"]

            cdb.set_document("campaigns", key, {"status": status})

    return HttpResponseRedirect("/scheduler/daily/" + day)
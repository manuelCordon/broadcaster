import time
import datetime
from DataAccess import ConfigDB, DataDB

__author__ = 'manuel'

def clean_up(ddb):
    data = DataDB(ddb)
    data.move_unique("raw_data", "data")

def execute_cleanup():
    cdb = ConfigDB()
    while True:
        print "Start clean loop at " + str(datetime.datetime.now())
        for campaign in list(cdb.get_collection("campaigns", {"status": "ready for cleanup"})):
            print str(datetime.datetime.now()) + " Start cleanup for campaign_id=" + str(campaign["_id"])
            ddb = str(campaign["_id"])
            clean_up(ddb)
            campaign["status"] = "ready for scheduler"
            cdb.set_campaign(campaign["_id"], campaign)
        print "  End clean loop at " + str(datetime.datetime.now())
        time.sleep(10)



execute_cleanup()
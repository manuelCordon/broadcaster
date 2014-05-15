import time
import datetime
from bson import ObjectId
from DataAccess import ConfigDB, DataDB
from im.core.config import configure, conf, configs
import logging
import sys
import os

__author__ = 'manuel'

# Load configuration files.
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))
configure(set_project_path=os.path.dirname(os.path.abspath(__file__)) + '/', override='PARTIAL')

# Run map reduce.
def clean_up(ddb):
    data = DataDB(ddb)
    data.move_unique("raw_data", "data")
    return data.count_documents("data")

# Execute the clean up.
def execute_cleanup():
    cdb = ConfigDB()
    while True:
        for campaign in list(cdb.get_collection("campaigns", {"status": "ready for cleanup"})):

            # Change status to cleaning.
            logging.info("({0}) campaign {1} Start cleanup".format(campaign["_id"], campaign["name"]))
            cdb.set_document("campaigns", campaign["_id"], {"status": "Cleaning the data"})

            # Perform clean up.
            ddb = str(campaign["_id"])
            volume = clean_up(ddb)

            # Update status and volume values.
            logging.info("({0}) campaign {1} ready for scheduler".format(campaign["_id"], campaign["name"]))
            cdb.set_document(
                "campaigns",
                campaign["_id"],
                {"volume": volume,
                 "status": "ready for scheduler"
                })

        logging.info("Sleep for 10 seconds...")
        time.sleep(10)


execute_cleanup()
import fnmatch
import time
import os
import zipfile
import csv
from bson import ObjectId
from dataAccess import ConfigDB
from dataAccess import DataDB
from im.core.config import configure, conf, configs
import logging
import sys

__author__ = 'manuel'

# Load configuration files.
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))
configure(set_project_path=os.path.dirname(os.path.abspath(__file__)) + '/', override='PARTIAL')

# Load configuration.
watch_folder = conf("config.watch_folder")
working_folder = conf("config.working_folder")
done_folder = conf("config.done_folder")
reject_folder = conf("config.reject_folder")
import_chunk_size = conf("config.import_chunk_size")

print watch_folder

# Instance config database handler.
cdb = ConfigDB()

# Extract the csv file from the zip file.
def get_csv(zip_filename):
    logging.debug("Unzipping " + zip_filename)
    fh = open(watch_folder + zip_filename, "rb")
    z = zipfile.ZipFile(fh)
    for inner_file in z.namelist():
        if fnmatch.fnmatch(inner_file, "*.csv"):
            z.extract(inner_file, working_folder)
            return working_folder + inner_file
    raise Exception("No csv found.")

# Insert csv content into data db.
def bulk_insert(db, csv_filename):
    i = 0
    b = []
    no_digits = 0
    data_db = DataDB(db)
    logging.debug("open " + csv_filename)
    with open(csv_filename, "rb") as csv_file:
        logging.debug("reading as csv")
        data_db.dispose_collection("raw_data")
        row_reader = csv.reader(csv_file)
        logging.debug("read as csv, start to scan the data")
        for row in row_reader:
            if len(row) == 0:
                logging.debug("Empty row")
            else:
                number = row[0]
                if not number.isdigit():  # validate if numeric
                    no_digits += 1
                else:
                    b.append({"_id": row[0]})
                    if len(b) > import_chunk_size:
                        data_db.bulk_import("raw_data", b)
                        start = i * import_chunk_size + 1
                        end = (i + 1) * import_chunk_size
                        logging.info("{0} imported records from {1} to {2}".format(db, start, end))
                        i += 1
                        b = []
        if len(b) > 0:
            data_db.bulk_import("raw_data", b)
            logging.info(db + " imported records from " + str(i * import_chunk_size + 1) + \
                " to " + str(i * import_chunk_size + 1 + len(b)) + " records")
        if no_digits > 0:
            logging.info(db + " " + str(no_digits) + " records where excluded because of illegal characters.")


def move_lists(campaign, list_type):

    list_type += "list"
    if list_type + "s" in campaign:
        # Create database handler.
        ddb = DataDB(campaign["_id"])

        # Destroy blacklist if exists.
        logging.debug("dispose old " + list_type)
        ddb.dispose_collection("blacklist")

        # Move all blacklists to data db.
        for l in campaign[list_type + "s"]:
            coll_name = "lst_{0}".format(l)
            logging.info("moving " + coll_name)
            ddb.bulk_import(list_type, cdb.get_collection(coll_name))
    else:
        logging.info("No {0} found".format(list_type))
    pass


def process_pending_campaigns():
    for filename in os.listdir(watch_folder):
        if fnmatch.fnmatch(filename, "camp_?*.zip"):
            try:
                campaign_id = ObjectId(filename[5:29])
                logging.debug("Campaign file {0} found".format(campaign_id))
                campaign = cdb.get_document("campaigns", where={"status": "ready for watcher", "_id": campaign_id})
                if campaign is None:
                    logging.WARNING(filename + " not found in db, moved the file to rejects folder.")
                    os.rename(watch_folder + filename, reject_folder + filename)
                else:
                    # Update status to importing data.
                    logging.debug("Import data")
                    campaign["status"] = "Importing data"
                    cdb.set_document("campaigns", campaign_id, campaign)
                    logging.debug("Begin data import for " + filename)

                    # Read the csv file and bulk import the data.
                    logging.debug("get csv")
                    csv_file = get_csv(filename)
                    bulk_insert(str(campaign_id), csv_file)

                    # Update status to black list/white list process.
                    campaign["status"] = "moving black list and white list"
                    cdb.set_document("campaigns", campaign_id, campaign)
                    move_lists(campaign, "black")
                    move_lists(campaign, "white")

                    # Delete the csv file and move the zip to done folder.
                    logging.debug("clear workspace")
                    os.rename(watch_folder + filename, done_folder + filename)
                    os.remove(csv_file)

                    # Set final state.
                    logging.debug("completed")
                    campaign["status"] = "ready for cleanup"
                    cdb.set_document("campaigns", campaign_id, campaign)

            except Exception, e:
                logging.error(e)


def process_bw_campaigns():
    for campaign in cdb.get_collection("campaigns", {"status": "ready for bw list import"}):

        # Update status to black list/white list process.
        campaign["status"] = "moving black list and white list"
        cdb.set_document("campaigns", campaign["_id"], campaign)
        move_lists(campaign, "black")
        move_lists(campaign, "white")

        # Set final state.
        logging.debug("completed")
        campaign["status"] = "ready for cleanup"
        cdb.set_document("campaigns", campaign["_id"], campaign)

def execute_watcher():
    while True:
        process_pending_campaigns()
        process_bw_campaigns()
        logging.info("Sleep 10 seconds...")
        time.sleep(10)


execute_watcher()
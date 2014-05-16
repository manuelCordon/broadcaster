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
    logging.trace("Unzipping " + zip_filename)
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
    logging.trace("open " + csv_filename)
    with open(csv_filename, "rb") as csv_file:
        logging.trace("reading as csv")
        data_db.dispose_collection("raw_data")
        row_reader = csv.reader(csv_file)
        logging.trace("read as csv, start to scan the data")
        for row in row_reader:
            if len(row) == 0:
                logging.trace("Empty row")
            else:
                number = row[0]
                if not number.isdigit():  # validate if numeric
                    no_digits += 1
                else:
                    b.append({"_id": row[0]})
                    if len(b) > import_chunk_size:
                        data_db.bulk_import("raw_data", b)
                        logging.info(db + " imported records from " + str(i * import_chunk_size + 1) + \
                            " to " + str((i + 1) * import_chunk_size))
                        i += 1
                        b = []
        if len(b) > 0:
            data_db.bulk_import("raw_data", b)
            print db + " imported records from " + str(i * import_chunk_size + 1) + \
                " to " + str(i * import_chunk_size + 1 + len(b)) + " records"
        if no_digits > 0:
            logging.info(db + " " + str(no_digits) + " records where excluded because of illegal characters.")


def move_blacklists(campaign):
    #ddb.dispose_collection("blacklists")
    #for blacklist in campaign["blacklists"]:
    #    ddb.bulk_import("blacklist", cdb.get_collection(blacklist))
    return


def process_pending_campaigns():
    for filename in os.listdir(watch_folder):
        if fnmatch.fnmatch(filename, "camp_?*.zip"):
            try:
                campaign_id = ObjectId(filename[5:29])
                campaign = cdb.get_document("campaigns", where={"status": "ready for watcher", "_id": campaign_id})
                if campaign is None:
                    logging.warning(filename + " not found in db, moved the file to rejects folder.")
                    os.rename(watch_folder + filename, reject_folder + filename)
                else:
                    # Update status to importing data.
                    logging.trace("Import data")
                    campaign["status"] = "Importing data"
                    cdb.set_document("campaigns", campaign_id, campaign)
                    logging.trace("Begin data import for " + filename)

                    # Read the csv file and bulk import the data.
                    logging.trace("get csv")
                    csv_file = get_csv(filename)
                    bulk_insert(str(campaign_id), csv_file)

                    # Delete the csv file and move the zip to done folder.
                    logging.trace("clear workspace")
                    os.rename(watch_folder + filename, done_folder + filename)
                    os.remove(csv_file)

                    # Update status to black list/white list process.
                    campaign["status"] = "moving black list and white list"
                    cdb.set_document("campaigns", campaign_id, campaign)

                    # Move the black list and white list.
                    # move_blacklists(campaign_id)

                    # Set final state.
                    logging.trace("completed")
                    campaign["status"] = "ready for cleanup"
                    cdb.set_document("campaigns", campaign_id, campaign)

            except Exception, e:
                logging.error("file error " + str(e))


def execute_watcher():
    while True:
        process_pending_campaigns()
        logging.info("Sleep 10 seconds...")
        time.sleep(10)


execute_watcher()
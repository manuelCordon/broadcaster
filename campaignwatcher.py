import fnmatch
import time
import os
import zipfile
import csv
from bson import ObjectId
from DataAccess import ConfigDB
from DataAccess import DataDB

__author__ = 'manuel'

watch_folder = "/home/manuel/"
working_folder = "/home/manuel/working/"
done_folder = "/home/manuel/done/"
reject_folder = "/home/manuel/rejects/"
import_chunk_size = 1000 * 100
cdb = ConfigDB()


def get_csv(zip_filename):
    print "Unzipping " + zip_filename
    fh = open(watch_folder + zip_filename, "rb")
    z = zipfile.ZipFile(fh)
    for inner_file in z.namelist():
        if fnmatch.fnmatch(inner_file, "*.csv"):
            z.extract(inner_file, working_folder)
            return working_folder + inner_file
    raise Exception("No csv found.")


def bulk_insert(db, csv_filename):
    i = 0
    b = []
    no_digits = 0
    data_db = DataDB(db)
    with open(csv_filename, "rb") as csvfile:
        data_db.drop_collection("raw_data")
        rowreader = csv.reader(csvfile)
        for row in rowreader:
            number = row[0]
            if not number.isdigit():  # validate if numeric
                no_digits += 1
            else:
                b.append({"_id": row[0]})
                if len(b) > import_chunk_size:
                    data_db.bulk_import("raw_data", b)
                    print db + " imported records from " + str(i * import_chunk_size + 1) + \
                        " to " + str((i + 1) * import_chunk_size)
                    i += 1
                    b = []
        if len(b) > 0:
            data_db.bulk_import("raw_data", b)
            print db + " imported records from " + str(i * import_chunk_size + 1) + \
                " to " + str(i * import_chunk_size + 1 + len(b)) + " records"
        if no_digits > 0:
            print db + " " + str(no_digits) + " records where excluded because of ilegal characters."


def move_blackists(db, campaign):
    ddb = DataDB(db)
    ddb.drop_collection("blacklists")
    for blacklist in campaign["blacklists"]:
        ddb.bulk_import("blacklist", cdb.getcollection(blacklist))
    return


def process_pending_campaigns():
    for filename in os.listdir(watch_folder):
        if fnmatch.fnmatch(filename, "camp_?*.zip"):
            try:
                campaign_id = ObjectId(filename[5:29])
                campaign = cdb.get_document("campaigns", where={"status": "ready for watcher", "_id": campaign_id})
                if campaign is None:
                    print filename + " not found in db."
                else:
                    csv_file = get_csv(filename)
                    bulk_insert(str(campaign_id), csv_file)
                    os.rename(watch_folder + filename, done_folder + filename)
                    os.remove(csv_file)
                    campaign["status"] = "ready for cleanup"
                    cdb.set_campaign(campaign_id, campaign)
            except Exception, e:
                print "Error '" + filename + "': %s" % e


def execute_watcher():
    while True:
        print "WATCHER: loop"
        process_pending_campaigns()
        print "WATCHER: end loop"
        time.sleep(10)


execute_watcher()
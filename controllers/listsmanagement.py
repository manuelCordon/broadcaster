import datetime
import json
import zipfile
import csv
import fnmatch
import logging
import io

from bson import ObjectId
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from Forms import *


__author__ = 'manuel'


# Shows the list based on the type specified.
@login_required
def show(request, list_type):
    # Check for the specific permission.
    if not request.user.has_perm("broadcaster.lists_view"):
        return render(request, "access_denied.html")

    # Get the message if any.
    if request.method == "GET":
        msg = request.GET.get("msg", None)
    else:
        msg = None

    # Get the lists by type from the database.
    lists = tuple(ConfigDB().get_collection("lists", {"type": list_type}))

    # Replace _id to list_id to be consumed by the template since no _ starting ids can be used.
    for l in lists:
        l["list_id"] = l.pop("_id")
        if not l.has_key("volume"):
            l["volume"] = "No file uploaded"
            l["upload_date"] = "N/A"

    return render(request,
                  "lists/list.html",
                  {"lists": lists,
                   "type": list_type,
                   "message": msg})


@csrf_exempt
@login_required
def json_items(request, list_type):
    if request.method == "POST":
        # Get the list of items to be displayed.
        lists = []
        for l in ConfigDB().get_collection("lists", {"type": list_type}):
            lists += [{"id": str(l["_id"]), "text": l["name"]}]
        #build response.
        response = {"q": request.POST["data[q]"],
                    "results": lists}

        # Convert to JSON.
        response = json.dumps(response)
        return HttpResponse(response, content_type='application/json')


# Allows to edit/add a list.
@login_required
def edit(request, list_type, _id=None):
    # Check for the specific permission.
    if not request.user.has_perm("broadcaster.lists_view"):
        return render(request, "access_denied.html")

    if _id is None:
        # No _id, generates an empty list.
        lst = ConfigDB().set_document("lists", None, {})
    else:
        # Reads the list from the db.
        lst = ConfigDB().get_document("lists",
                                       {"type": list_type,
                                        "_id": ObjectId(_id)})
    # Replaces _id with list_id.
    lst["list_id"] = lst.pop("_id")

    # Preload the form to be submitted.
    frm = ListForm(initial=lst)

    return render(request,
                  "lists/edit.html",
                  {"type": list_type,
                   "form": frm})


# Removes the list from the system.
@login_required
def remove(request, list_type, _id):
    # Check for the specific permission.
    if not request.user.has_perm("broadcaster.lists_delete"):
        return render(request, "access_denied.html")

    ConfigDB().dispose_document("lists",
                                {"type": list_type,
                                 "_id": ObjectId(_id)})
    return HttpResponseRedirect("/lists/{0}?msg=delete_ok".format(list_type))


# Removes the lists without type from the system silently.
@login_required
def discard(request, list_type):
    ConfigDB().dispose_document("lists",
                                {"type": {"$exists": False}})
    return HttpResponseRedirect("/lists/" + list_type)


# Save the campaign into the database.
@csrf_exempt
@login_required
def save(request, list_type):
    # Check for the specific permission.
    if not request.user.has_perm("broadcaster.lists_edit"):
        return render(request, "access_denied.html")

    if request.method == "POST":
        f = request.POST

        # Try to retrieve campaign from db, if not possible generate an empty campaign.
        try:
            _id = ObjectId(str(f["list_id"]))
            l = ConfigDB().get_document("lists", {"_id": _id})
        except:
            _id = None
            l = {}

        # Assign new values.
        l["_id"] = _id
        l["type"] = list_type
        l["name"] = f.get("name")
        l["comment"] = f.get("comment")

        # Save in the db.
        ConfigDB().set_document("lists", _id, l)
        return HttpResponseRedirect("/lists/{0}?msg=save_ok".format(list_type))


# Upload file and process.
# Receives the ajax request to upload the file.
@csrf_exempt
@login_required
def upload_file(request):
    # Check for the specific permission.
    if not request.user.has_perm("broadcaster.lists_edit"):
        return render(request, "access_denied.html")

    if request.method == 'POST':

        # Get campaign id if available.
        logging.info("Received post to upload file for {0}".format(request.POST.get("list_id", "")))
        list_id = ObjectId(request.POST.get("list_id"))

        # Update list document with upload date.
        logging.info("Adding list upload date.")
        c = ConfigDB().set_document("campaigns",
                                    list_id,
                                    {"upload_date": datetime.datetime.now().isoformat()})

        # Process the file in the server.
        process_file(request.FILES['fileToUpload'], list_id)

        # Return OK message.
        return render(request, "blank.html", {"message": "OK"})


# Unzip the file and import the csv data to the list collection.
def process_file(file_content, _id):
    print " Processing the file."
    # Unzip the content.
    zip_file = zipfile.ZipFile(file_content)
    data = []
    print " Created zip object, scanning the content."
    for inner_file in zip_file.namelist():
        if fnmatch.fnmatch(inner_file, "*.csv"):
            print " CSV found: " + inner_file
            row_reader = csv.reader(io.BytesIO(zip_file.read(inner_file)))
            print " csv reader created."
            for row in row_reader:
                print(row)
                if len(row) == 0:
                    print "Empty row"
                else:
                    number = row[0]
                    if number.isdigit():  # validate if numeric
                        data.append({"_id": row[0]})

            # Config db handler and build collection names.
            cdb = ConfigDB()
            lst_coll = "lst_{0}".format(_id)

            # Import, remove duplicates and remove the raw collection.
            print("importing")
            cdb.bulk_import(lst_coll, data)

            cdb.set_document("lists",
                             _id,
                             {"volume": cdb.count_documents(lst_coll),
                              "upload_date": datetime.datetime.now().isoformat()})

            print("All done.")
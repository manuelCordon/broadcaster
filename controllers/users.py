from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from Forms import UserForm
from data.mysql_data_access import AuthenticationDB


__author__ = 'manuel'


# Shows the list based on the type specified.
@login_required
def show(request):
    # Check for the specific permission.
    if not request.user.has_perm("broadcaster.users_manage"):
        return render(request, "access_denied.html")

    # Get the message if any.
    if request.method == "GET":
        msg = request.GET.get("msg", None)
    else:
        msg = None

    # Get the lists by type from the database.
    users = AuthenticationDB().get_users()
    return render(request,
                  "user/list.html",
                  {"users": users,
                   "message": msg})


# Allows add/edit users.
@login_required
def edit(request, _id=None):
    # Check for the specific permission.
    if not request.user.has_perm("broadcaster.users_manage"):
        return render(request, "access_denied.html")

    if _id is None:
        # No _id, uses an empty form.
        frm = UserForm()
    else:
        # Reads the user from the db.
        usr = AuthenticationDB().get_user(_id)

        print(usr)

        # Preload the user details.
        frm = UserForm(initial=usr)

    return render(request, "user/edit.html", {"form": frm})


# Persist the changes made to the user.
@csrf_exempt
@login_required
def save(request):
    # Check for the specific permission.
    if not request.user.has_perm("broadcaster.users_manage"):
        return render(request, "access_denied.html")

    if request.method == "POST":
        frm = request.POST
        if frm["id"] != "":
            # Update metadata from the user.
            u = User.objects.get(username=frm["username"])
            u.first_name = frm["first_name"]
            u.last_name = frm["last_name"]
            u.email = frm["email"]

            # If password change, send an email.
            if frm.get("generate_password", "off") == "on":
                pwd = User.objects.make_random_password()
                u.set_password(pwd)
                u.email_user(subject="Password change",
                             message="The password for {0} account was changed to: {1}.".format(frm["username"], pwd))
            elif len(frm["password1"]) > 0 and frm["password1"] == frm["password2"]:
                u.set_password(frm["password1"])
                #u.email_user(subject="Password change",
                #             message="The password for {0} account was changed to: {1}.".format(frm["username"], frm["password1"]))
            u.save()

            # Update group assignation.
            u.groups.clear()
            for group_id in frm.getlist("groups"):
                print(">>> assign group " + group_id)
                u.groups.add(Group.objects.get(id=group_id))
        else:
            # Create user.
            u = User.objects.create(username=frm["username"],
                                    first_name=frm["first_name"],
                                    last_name=frm["last_name"],
                                    email=frm["email"])

            # If password change, send an email.
            if frm.get("generate_password", "off") == "on":
                pwd = User.objects.make_random_password()
                u.set_password(pwd)
                u.email_user(subject="Password change",
                             message="The password for {0} account was changed to: {1}.".format(frm["username"], pwd))
            elif len(frm["password1"]) > 0 and frm["password1"] == frm["password2"]:
                u.set_password(frm["password1"])
                #u.email_user(subject="Password change",
                #             message="The password for {0} account was changed to: {1}.".format(frm["username"], frm["password1"]))
            u.save()

            # Assign groups.
            for group_id in frm.getlist("groups"):
                print(">>> assign group " + group_id)
                u.groups.add(Group.objects.get(id=group_id))

        return HttpResponseRedirect("/user/list??msg=save_ok")
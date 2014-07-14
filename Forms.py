from django import forms

from data.mongo_data_access import ConfigDB
from data.mysql_data_access import AuthenticationDB


__author__ = 'manuel'


class UploadFileForm(forms.Form):
    name = forms.CharField(max_length=250, required=True)
    start_date = forms.DateTimeField()


class CampaignForm(forms.Form):
    name = forms.CharField(
        required=True,
        max_length=250,
        widget=forms.TextInput({
            "class": "form-control",
            "placeholder": "Nombre"
        })
    )

    file_name = forms.CharField(
        max_length=100,
        label="Nombre del archivo",
        widget=forms.TextInput({
            "class": "form-control",
            "placeholder": "Nombre del archivo"
        })
    )

    owner = forms.ChoiceField(
        choices=ConfigDB().get_users(role="owner"),
        required=False,
        widget=forms.Select({"class": "form-control chosen-select"})

    )

    category = forms.ChoiceField(
        choices=ConfigDB().get_categories(),
        widget=forms.Select({"class": "form-control chosen-select"}),
        required=False
    )

    product = forms.ChoiceField(
        choices=ConfigDB().get_products(),
        widget=forms.Select({"class": "form-control chosen-select"}),
        required=False
    )


    message = forms.CharField(
        max_length=160,
        label="Mensaje",
        widget=forms.TextInput({
            "class": "form-control",
            "placeholder": "Mensaje",
        })

    )

    destination = forms.ChoiceField(
        choices=ConfigDB().get_destinations(),
        widget=forms.Select({"class": "chosen-select form-control"}),
        required=False
    )

    start_date = forms.DateTimeField(
        required=True,
        widget=forms.TextInput({"class": "form-control", "data-date-format": "yyyy-mm-dd"})
    )

    end_date = forms.DateTimeField(
        required=True,
        widget=forms.DateInput({"class": "form-control"})
    )

    priority = forms.ChoiceField(
        choices=ConfigDB().get_priorities(),
        widget=forms.Select({"class": "chosen-select form-control"}),
        required=False
    )

    authorization_required = forms.BooleanField(
        widget=forms.CheckboxInput()
    )

    blacklists = forms.MultipleChoiceField(
        label="Listas negras",
        choices=ConfigDB().get_blacklists(),
        widget=forms.SelectMultiple({"class": "form-control"})
    )

    whitelists = forms.MultipleChoiceField(
        label="Listas blancas",
        choices=ConfigDB().get_whitelists(),
        widget=forms.SelectMultiple({"class": "form-control"})
    )

    #Hidden fields
    campaign_id = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(CampaignForm, self).__init__(*args, **kwargs)


class ListForm(forms.Form):

    name = forms.CharField(
        required=True,
        max_length=250,
        widget=forms.TextInput({
            "class": "form-control",
            "placeholder": "Nombre"
        })
    )

    comment = forms.CharField(
        required=True,
        max_length=500,
        widget=forms.TextInput({
            "class": "form-control",
            "placeholder": "Comentario"
        })
    )

    #Hidden fields
    list_id = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(ListForm, self).__init__(*args, **kwargs)


class UserForm(forms.Form):

    username = forms.CharField(
        required=True,
        max_length=250,
        widget=forms.TextInput({
            "class": "form-control",
            "placeholder": "Username"
        })
    )

    first_name = forms.CharField(
        required=True,
        max_length=250,
        widget=forms.TextInput({
            "class": "form-control",
            "placeholder": "Nombre de usuario"
        })
    )

    last_name = forms.CharField(
        required=True,
        max_length=250,
        widget=forms.TextInput({
            "class": "form-control",
            "placeholder": "Apellido del usuario"
        })
    )

    email = forms.CharField(
        required=True,
        max_length=250,
        widget=forms.TextInput({
            "class": "form-control",
            "placeholder": "Direccion de correo"
        })
    )

    groups = forms.MultipleChoiceField(
        choices=AuthenticationDB().get_groups(),
        widget=forms.SelectMultiple({"class": "chosen-select form-control"})
    )

    generate_password = forms.BooleanField(
        widget=forms.CheckboxInput()
    )

    password1 = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.PasswordInput({"class": "form-control"})
    )

    password2 = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.PasswordInput({"class": "form-control"})
    )

    # Hidden fields
    id = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
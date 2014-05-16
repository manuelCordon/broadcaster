from dataAccess import ConfigDB
from django import forms

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

    ignore_max_sms_policy = forms.BooleanField(
        widget=forms.Select(
            attrs={"class": "chosen-select"},
            choices=((True, 'Si'), (False, 'No'))
        )
    )

    blacklists = forms.MultipleChoiceField(
        label="Listas negras",
        widget=forms.Select({"class": "chosen-select form-control", "multiple": ""}),
        choices=ConfigDB().get_blacklists()
    )

    whitelists = forms.MultipleChoiceField(
        label="Listas blancas",
        widget=forms.Select({"class": "chosen-select form-control", "multiple": ""}),
        choices=ConfigDB().get_whitelists()
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
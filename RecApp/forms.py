from django import forms

class get_reco_form(forms.Form):
    name = forms.CharField(required=True)
    cuisine = forms.CharField(required=True)
    location = forms.CharField(required=True)

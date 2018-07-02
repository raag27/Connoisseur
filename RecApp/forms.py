from django import forms
from django.core.validators import RegexValidator

alpha = RegexValidator(r'^[0-5]*$', 'enter your preference value[0-5]')
num = RegexValidator(r'^[0-4].[0-9]*','enter your rating [0-5]')
class get_reco_form(forms.Form):
    name = forms.CharField(required=True)
    cuisine = forms.IntegerField(required=True,max_value=5,min_value=0,validators=[alpha])
    location = forms.IntegerField(required=True,max_value=5,min_value=0,validators=[alpha])
    price = forms.IntegerField(required = True,max_value=5,min_value=0,validators=[alpha])
    class Meta:
        fields = ['name','cuisine','location','price']


class rate_rest_form(forms.Form):
    username = forms.CharField(required=True)
    restaurant_name = forms.CharField(required=True)
    rating = forms.FloatField(required=True,min_value=0,max_value=5)
    location = forms.CharField(required=True)

    class Meta:
        fields = ['username','restaurant_name','location','rating']

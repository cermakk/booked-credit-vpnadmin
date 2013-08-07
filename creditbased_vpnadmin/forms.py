# -*- coding: utf-8 -*-
import datetime
from django import forms


class BillUploadForm(forms.Form):
    bill = forms.FileField()
    day = forms.DateField(initial=datetime.date.today())
    

class PricesSelectForm(forms.Form):
    call = forms.FloatField()
    sms = forms.FloatField()
    mms = forms.FloatField()
__author__ = 'juanfranfv'
from django import forms
from models import *

class InscripcionBaseForm(forms.ModelForm):
    class Meta:
        model = InscripcionBase
        exclude = ['datos','actividad']


class InscriptoInfo(forms.ModelForm):
    class Meta:
        model = InscripcionBase
        exclude = ['id']


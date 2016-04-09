__author__ = 'juanfranfv'
from django import forms
from models import *

class InscripcionBaseForm(forms.ModelForm):
    class Meta:
        model = Inscripcion_Base
        exclude = ['datos','actividad']


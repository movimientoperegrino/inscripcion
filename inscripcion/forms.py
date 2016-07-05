# -*- coding: utf-8 -*-
__author__ = 'juanfranfv'


from django import forms
from models import *

class InscripcionBaseForm(forms.ModelForm):
    confirmacion_mail = forms.EmailField(label="Confirmación del mail")
    class Meta:
        model = InscripcionBase
        exclude = ['datos','actividad','puesto']

    def clean(self):
        cleaned_data = super(InscripcionBaseForm, self).clean()
        mail = cleaned_data.get("mail")
        confirmacion_mail = cleaned_data.get("confirmacion_mail")

        if mail != confirmacion_mail:
            raise forms.ValidationError(
                "Los mails deben ser iguales"
            )

class InscriptoInfo(forms.ModelForm):
    class Meta:
        model = InscripcionBase
        exclude = ['id']


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        exclude = ['id']


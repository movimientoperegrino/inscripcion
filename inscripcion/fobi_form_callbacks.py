__author__ = 'juanfranfv'
import json
from fobi.constants import (
    CALLBACK_BEFORE_FORM_VALIDATION,
    CALLBACK_FORM_VALID_BEFORE_SUBMIT_PLUGIN_FORM_DATA,
    CALLBACK_FORM_VALID, CALLBACK_FORM_VALID_AFTER_FORM_HANDLERS,
    CALLBACK_FORM_INVALID
    )
from fobi.base import FormCallback, form_callback_registry

class InscripcionCallback(FormCallback):
    stage = CALLBACK_FORM_VALID

    def callback(self, form_entry, request, form):
        print(json.dumps(form.cleaned_data))
        print(form.cleaned_data)
        print(self)
        print(form_entry)
        print(request)
        print(form)

form_callback_registry.register(InscripcionCallback)
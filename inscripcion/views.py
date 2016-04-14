from django.shortcuts import render

# Create your views here.
import datetime
from models import *
from forms import *
import logging
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
import simplejson as json

from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.decorators import login_required, permission_required
from django.db import models, IntegrityError
from django.utils.datastructures import MultiValueDictKeyError

from fobi.models import FormEntry, FormElementEntry, FormHandlerEntry
from fobi.forms import (
    FormEntryForm, FormElementEntryFormSet, ImportFormEntryForm
)
from fobi.dynamic import assemble_form_class
from fobi.decorators import permissions_required, SATISFY_ALL, SATISFY_ANY
from fobi.base import (
    fire_form_callbacks, run_form_handlers, form_element_plugin_registry,
    form_handler_plugin_registry, submit_plugin_form_data, get_theme, get_processed_form_data
    #get_registered_form_handler_plugins
)
from fobi.form_importers import (
    form_importer_plugin_registry, get_form_impoter_plugin_urls,
    ensure_autodiscover as ensure_importers_autodiscover
)
from fobi.constants import (
    CALLBACK_BEFORE_FORM_VALIDATION,
    CALLBACK_FORM_VALID_BEFORE_SUBMIT_PLUGIN_FORM_DATA,
    CALLBACK_FORM_VALID, CALLBACK_FORM_VALID_AFTER_FORM_HANDLERS,
    CALLBACK_FORM_INVALID
)
from fobi.utils import (
    get_user_form_field_plugin_uids,
    #get_user_form_element_plugins,
    get_user_form_element_plugins_grouped,
    #get_user_form_handler_plugins_grouped,
    get_user_form_handler_plugins, get_user_form_handler_plugin_uids,
    append_edit_and_delete_links_to_field
)
from fobi.helpers import JSONDataExporter
from fobi.settings import GET_PARAM_INITIAL_DATA, DEBUG

logger = logging.getLogger(__name__)

def info_inscripto(request, idInscripto):
    inscripto = get_object_or_404(InscripcionBase, pk=idInscripto)
    dato = json.loads(inscripto.datos)
    print(dato)
    print(dato['peregrino_que_te_invito'])
    return HttpResponse("Hello, world. You're at the polls index.")

def form(request, form_entry_slug, theme=None, template_name=None):
    """
    View create form.

    :param django.http.HttpRequest request:
    :param string form_entry_slug:
    :param fobi.base.BaseTheme theme: Theme instance.
    :param string template_name:
    :return django.http.HttpResponse:
    """
    try:
        kwargs = {'slug': form_entry_slug}
        if not request.user.is_authenticated():
            kwargs.update({'is_public': True})
        form_entry = FormEntry._default_manager.select_related('user') \
                              .get(**kwargs)
    except ObjectDoesNotExist as err:
        raise Http404(ugettext("Form entry not found."))

    form_element_entries = form_entry.formelemententry_set.all()[:]

    # This is where the most of the magic happens. Our form is being built
    # dynamically.
    FormClass = assemble_form_class(
        form_entry,
        form_element_entries = form_element_entries,
        request = request
    )

    if request.method == 'POST':
        print("guardo")
    else:
        # Providing initial form data by feeding entire GET dictionary
        # to the form, if ``GET_PARAM_INITIAL_DATA`` is present in the
        # GET.
        kwargs = {}
        #if GET_PARAM_INITIAL_DATA in request.GET:
            #kwargs = {'initial': request.GET}
        form = FormClass(**kwargs)


    context = {
        'form': form,
    }


    return render_to_response('form.html', context,
                              context_instance=RequestContext(request))


def inscripcion_actividad(request, idActividad):
    actividad = get_object_or_404(Actividad, pk=idActividad)
    if request.method == 'POST':
        inscripcion = InscripcionBase()
        inscripcion.actividad = actividad
        form = InscripcionBaseForm(request.POST, instance=inscripcion)
        if form.is_valid():
            inscripto = form.save()
            return HttpResponseRedirect('/inscripto/' + str(inscripto.id))


    else:
        form = InscripcionBaseForm()

    context = {
        'form': form,
    }


    return render_to_response('form.html', context,
                              context_instance=RequestContext(request))

def inscripcion_extra(request, idInscripto):
    inscripto = get_object_or_404(InscripcionBase, pk=idInscripto)
    form_entry = inscripto.actividad.detalle

    form_element_entries = form_entry.formelemententry_set.all()[:]
    # This is where the most of the magic happens. Our form is being built
    # dynamically.
    FormClass = assemble_form_class(
        form_entry,
        form_element_entries = form_element_entries,
        request = request
    )

    if 'POST' == request.method:
        form = FormClass(request.POST, request.FILES)


        if form.is_valid():
            field_name_to_label_map, cleaned_data = get_processed_form_data(
            form,
            form_element_entries
            )
            for key, value in cleaned_data.items():
                if isinstance(value, (datetime.datetime, datetime.date)):
                    cleaned_data[key] = value.isoformat() if hasattr(value, 'isoformat') else value
            inscripto.datos = json.dumps(cleaned_data)
            inscripto.save()

            messages.info(
                request,
                _("Form {0} was submitted successfully."
                  "").format(form_entry.name)
            )
            return redirect(
                reverse('fobi.form_entry_submitted', args=[form_entry.slug])
            )


    else:
        # Providing initial form data by feeding entire GET dictionary
        # to the form, if ``GET_PARAM_INITIAL_DATA`` is present in the
        # GET.
        kwargs = {}
        if GET_PARAM_INITIAL_DATA in request.GET:
            kwargs = {'initial': request.GET}
        form = FormClass(**kwargs)

    # In debug mode, try to identify possible problems.
    if DEBUG:
        try:
            form.as_p()
        except Exception as err:
            logger.error(err)


    context = {
        'form': form,
    }


    return render_to_response('form.html', context,
                              context_instance=RequestContext(request))

def view_form_entry(request, form_entry_slug, theme=None, template_name=None):
    """
    View create form.

    :param django.http.HttpRequest request:
    :param string form_entry_slug:
    :param fobi.base.BaseTheme theme: Theme instance.
    :param string template_name:
    :return django.http.HttpResponse:
    """
    try:
        kwargs = {'slug': form_entry_slug}
        if not request.user.is_authenticated():
            kwargs.update({'is_public': True})
        form_entry = FormEntry._default_manager.select_related('user') \
                              .get(**kwargs)
    except ObjectDoesNotExist as err:
        raise Http404(ugettext("Form entry not found."))

    form_element_entries = form_entry.formelemententry_set.all()[:]

    # This is where the most of the magic happens. Our form is being built
    # dynamically.
    FormClass = assemble_form_class(
        form_entry,
        form_element_entries = form_element_entries,
        request = request
    )

    if 'POST' == request.method:
        form = FormClass(request.POST, request.FILES)

        # Fire pre form validation callbacks
        fire_form_callbacks(form_entry=form_entry, request=request, form=form,
                            stage=CALLBACK_BEFORE_FORM_VALIDATION)

        if form.is_valid():
            # Fire form valid callbacks, before handling submitted plugin
            # form data.
            form = fire_form_callbacks(
                form_entry = form_entry,
                request = request,
                form = form,
                stage = CALLBACK_FORM_VALID_BEFORE_SUBMIT_PLUGIN_FORM_DATA
            )

            # Fire plugin processors
            form = submit_plugin_form_data(form_entry=form_entry,
                                           request=request, form=form)

            # Fire form valid callbacks
            form = fire_form_callbacks(form_entry=form_entry,
                                       request=request, form=form,
                                       stage=CALLBACK_FORM_VALID)

            # Run all handlers
            handler_responses, handler_errors = run_form_handlers(
                form_entry = form_entry,
                request = request,
                form = form,
                form_element_entries = form_element_entries
            )

            # Warning that not everything went ok.
            if handler_errors:
                for handler_error in handler_errors:
                    messages.warning(
                        request,
                        _("Error occured: {0}."
                          "").format(handler_error)
                    )

            # Fire post handler callbacks
            fire_form_callbacks(
                form_entry = form_entry,
                request = request,
                form = form,
                stage = CALLBACK_FORM_VALID_AFTER_FORM_HANDLERS
                )

            messages.info(
                request,
                _("Form {0} was submitted successfully."
                  "").format(form_entry.name)
            )
            return redirect(
                reverse('fobi.form_entry_submitted', args=[form_entry.slug])
            )
        else:
            # Fire post form validation callbacks
            fire_form_callbacks(form_entry=form_entry, request=request,
                                form=form, stage=CALLBACK_FORM_INVALID)

    else:
        # Providing initial form data by feeding entire GET dictionary
        # to the form, if ``GET_PARAM_INITIAL_DATA`` is present in the
        # GET.
        kwargs = {}
        if GET_PARAM_INITIAL_DATA in request.GET:
            kwargs = {'initial': request.GET}
        form = FormClass(**kwargs)

    # In debug mode, try to identify possible problems.
    if DEBUG:
        try:
            form.as_p()
        except Exception as err:
            logger.error(err)

    theme = get_theme(request=request, as_instance=True)
    theme.collect_plugin_media(form_element_entries)

    context = {
        'form': form,
        'form_entry': form_entry,
        'fobi_theme': theme,
    }

    if not template_name:
        template_name = theme.view_form_entry_template

    return render_to_response(template_name, context,
                              context_instance=RequestContext(request))
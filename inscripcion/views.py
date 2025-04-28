# -*- coding: utf-8 -*-

from django.shortcuts import render

# Create your views here.
import datetime
from datetime import timedelta
from django.utils import timezone
from .models import *
from .forms import *
import logging

import simplejson as json

from django.template import RequestContext
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext, gettext_lazy as _
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

from fobi.settings import GET_PARAM_INITIAL_DATA, DEBUG
import csv
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm

from django.core.cache import cache
from functools import lru_cache
from django.conf import settings

logger = logging.getLogger(__name__)

def info_inscripto(request):
    m = request.GET.get('m')
    text = request.GET.get('text')
    inscripto_id = decode_data(m, text)
    inscripto = InscripcionBase.objects.get(id=inscripto_id)
    form = InscriptoInfo(instance=inscripto)
    context = {'form': form}
    return render(request, 'form.html', context)



def iniciar_sesion(request):
    mensaje =""
    if not request.user.is_anonymous:
        return HttpResponseRedirect('/actividades')
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        if form.is_valid:
            usuario = request.POST['username']
            clave = request.POST['password']
            acceso = authenticate(username=usuario, password=clave)
            if acceso is not None:
                if acceso.is_active:
                    login(request, acceso)
                    return lista_actividades(request)
            else:
                mensaje = u"Credenciales incorrectas"

    else:
        form = AuthenticationForm()
    return render(request, 'admin/login.html', {'form': form, 'mensaje': mensaje})

def cerrar_sesion(request):
    logout(request)
    return HttpResponseRedirect('/login')

@login_required(login_url='/login')
def lista_actividades(request):
    actividades = Actividad.objects.all().order_by('-fechaApertura')
    for a in actividades:
        print(a.fechaApertura)
    return render(
        request,
        'admin/actividad_list.html',
        {'lista_actividades': actividades}
    )



@login_required(login_url='/login')
def nueva_actividad(request):
    if request.method == 'POST':
        form = ActividadForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/login')
    else:
        form = ActividadForm()

    titulo = 'Nueva actividad'
    return render(
        request,
        'admin/form.html',
        {'form': form, 'titulo': titulo},
    )

@login_required(login_url='/login')
def editar_actividad(request, id_actividad):
    try:
        actividad = Actividad.objects.get(pk=id_actividad)
    except Actividad.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        form = ActividadForm(request.POST, instance=actividad)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/actividades')

    else:
        form = ActividadForm(instance=actividad)

    titulo = 'Editar actividad: ' + actividad.nombre
    return render(
        request,
        'admin/form.html',
        {'form': form, 'titulo': titulo},
    )

@login_required(login_url='/login')
def eliminar_actividad(request, id_actividad):
    try:
        actividad = Actividad.objects.get(pk=id_actividad)
    except Actividad.DoesNotExist:
        raise Http404
    return render(
        request,
        'admin/eliminar_actividad.html',
        {'actividad': actividad},
    )

@login_required(login_url='/login')
def actividad_eliminada(request, id_actividad):
    try:
        actividad = Actividad.objects.get(pk=id_actividad)
    except Actividad.DoesNotExist:
        raise Http404
    mensaje = u"La actividad " + actividad.nombre + u" ha sido eliminada con éxito."
    actividad.delete()
    actividades = Actividad.objects.all().order_by('fechaApertura').reverse()
    return render(
        request,
        'admin/actividad_list.html',
        {'mensaje': mensaje, 'lista_actividades': actividades},
    )


@login_required(login_url='/login')
def url_inscripcion_extra(request, id_inscripto):
    m, txt = encode_data(str(id_inscripto))
    #url_info = request.scheme + '://' + request.META['HTTP_HOST'] + '/inscripto?m="' + m + '"&text="' + txt +'"'
    url_info = request.scheme + '://' + request.META['HTTP_HOST'] + '/inscripto?m=' + urllib.parse.quote(m) + '&text=' + urllib.parse.quote(txt)
    messages.info(request, url_info)
    inscripto = get_object_or_404(InscripcionBase, pk=id_inscripto)
    return inscriptos_actividad(request, inscripto.actividad.id)


@login_required(login_url='/login')
def inscriptos_actividad(request, idActividad):
    actividad = get_object_or_404(Actividad, pk=idActividad)
    # print actividad
    # m, txt = encode_data(idActividad)
    # print m
    # print txt
    # url_info = request.scheme + '://' + request.META['HTTP_HOST'] + '/inscriptos?m=' + m + '&text=' + txt
    # return HttpResponseRedirect(url_info)
    form_entry = actividad.formDinamico

    form_element_entries = form_entry.formelemententry_set.all()[:]
    cabecera = []
    jsontitles=[]
    for entry in form_element_entries:
        aux = json.loads(entry.plugin_data)
        cabecera.append(aux["label"])
        jsontitles.append(aux["name"])
    lista_inscriptos = InscripcionBase.objects.filter(actividad=actividad).order_by('puesto')
    for inscripto in lista_inscriptos:
        if inscripto.datos != None:
            inscripto.datos = json.loads(inscripto.datos)
    m, txt = encode_data(str(actividad.id))
    url_contacto = request.scheme + '://' + request.META['HTTP_HOST'] + '/inscriptos?m=' + urllib.parse.quote(m) + '&text=' + urllib.parse.quote(txt)
    url_csv = request.scheme + '://' + request.META['HTTP_HOST'] + '/csv?m=' + urllib.parse.quote(m) + '&text=' + urllib.parse.quote(txt)
    context = {'lista_inscriptos': lista_inscriptos,
               'actividad': actividad,
               'cabecera': cabecera,
               'jsontitles': jsontitles,
               'url_contacto': url_contacto,
               'url_csv': url_csv,
               }
    return render(request, 'admin/inscriptos.html', context)


def lista_inscriptos(request):
    m = request.GET.get('m')
    text = request.GET.get('text')
    try:
        actividad_id = decode_data(m, text)
    except:
        mensaje = u'La url no es correcta.'
        return render(
            request,
            'error.html',
            {'mensaje': mensaje},
        )
    actividad = get_object_or_404(Actividad, pk=actividad_id)
    form_entry = actividad.formDinamico

    form_element_entries = form_entry.formelemententry_set.all()[:]
    cabecera = []
    jsontitles=[]
    for entry in form_element_entries:
        aux = json.loads(entry.plugin_data)
        cabecera.append(aux["label"])
        jsontitles.append(aux["name"])
    lista_inscriptos = InscripcionBase.objects.filter(actividad=actividad).order_by('puesto')
    for inscripto in lista_inscriptos:
        if inscripto.datos != None:
            inscripto.datos = json.loads(inscripto.datos)

    url_csv = request.scheme + '://' + request.META['HTTP_HOST'] + '/csv?m=' + urllib.parse.quote(m) + '&text=' + urllib.parse.quote(text)
    context = {'lista_inscriptos': lista_inscriptos,
               'actividad': actividad,
               'cabecera': cabecera,
               'jsontitles': jsontitles,
               'url_csv': url_csv,
               }
    return render(request, 'inscriptos.html', context)


def descargar_csv(request):
    m = request.GET.get('m')
    text = request.GET.get('text')
    try:
        actividad_id = decode_data(m, text)
    except:
        mensaje = u'La url no es correcta.'
        return render(
            request,
            'error.html',
            {'mensaje': mensaje},
        )
    actividad = get_object_or_404(Actividad, pk=actividad_id)
    form_entry = actividad.formDinamico

    form_element_entries = form_entry.formelemententry_set.all()[:]

    lista_inscriptos = InscripcionBase.objects.filter(actividad=actividad).order_by('puesto')
    for inscripto in lista_inscriptos:
        if inscripto.datos != None:
            inscripto.datos = json.loads(inscripto.datos)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inscriptos.csv"'

    writer = csv.writer(response, delimiter=';')
    row = ['Puesto', 'Nombre', 'Apellido', 'Cedula', 'Telefono', 'Email']
    jsontitles=[]
    for entry in form_element_entries:
        aux = json.loads(entry.plugin_data)
        jsontitles.append(aux["name"])
        row.append(aux["label"].encode('utf-8'))
    row.append('Fecha de inscripcion')
    writer.writerow(row)

    for inscripto in lista_inscriptos:
        row = [inscripto.puesto, inscripto.nombre.encode('utf-8'), inscripto.apellido.encode('utf-8'),
               inscripto.cedula.encode('utf-8'), inscripto.celular.encode('utf-8'), inscripto.mail.encode('utf-8')]
        for dato in jsontitles:
            try:
                if(isinstance(inscripto.datos[dato], str)):
                    row.append(inscripto.datos[dato].encode('utf-8'))
                else:
                    row.append(str(inscripto.datos[dato]))
            except:
                row.append("".encode('utf-8'))
        row.append(inscripto.fechaInscripcion)
        writer.writerow(row)

    return response


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
        raise Http404(gettext("Form entry not found."))

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


    return render(request, 'form.html', context)



def inscripcion_actividad(request, idActividad):
    actividad = get_object_or_404(Actividad, pk=idActividad)

    #si el estado de la actividad es finalizado, termina la inscripcion
    if actividad.estado == Actividad.FINALIZADO:
        mensaje = u'La inscripción a la actividad: "' + actividad.nombre + u'" ha finalizado o se ha llenado'
        messages.warning(request, mensaje)
        return HttpResponseRedirect(reverse('inicio'))

    #se controla la cantidad de inscriptos
    cantidadPermitida = actividad.cantidadSuplentes + actividad.cantidadTitulares
    cantidadInscriptos = InscripcionBase.objects.filter(actividad=actividad).count()
    if cantidadInscriptos >= cantidadPermitida:
        actividad.estado = actividad.FINALIZADO
        actividad.save()
        mensaje = u'La inscripción a la actividad: "' + actividad.nombre + u'" ha finalizado o se ha llenado'
        messages.warning(request, mensaje)
        return HttpResponseRedirect(reverse('inicio'))

    # se controla la fecha/hora de cierre
    if timezone.now() > actividad.fechaCierre:
        mensaje = u'La inscripción a la actividad: "' + actividad.nombre + u'" ha finalizado.'
        if actividad.estado != actividad.FINALIZADO:
            actividad.estado = actividad.FINALIZADO
            actividad.save()
        return HttpResponseRedirect(reverse('inicio'))

    #se controla la fecha/hora de activacion
    if timezone.now() < actividad.fechaApertura:
        mensaje = u'La inscripción a  la actividad "' + actividad.nombre + u'" aún no se encuentra habilitada'
        messages.warning(request, mensaje)
        return HttpResponseRedirect(reverse('inicio'))
    else:
        if actividad.estado == Actividad.INACTIVO:
            actividad.estado = Actividad.ACTIVO
            actividad.save()

    print(request.get_full_path())
    if request.method == 'POST':
        inscripcion = InscripcionBase()
        inscripcion.actividad = actividad
        inscripcion.puesto = InscripcionBase.objects.filter(actividad=actividad).count() + 1
        form = InscripcionBaseForm(request.POST, instance=inscripcion)
        if form.is_valid():
            cedula_raw = form.cleaned_data['cedula']
            cedula = ''.join(e for e in cedula_raw if e.isalnum())

            #Si ciBoolean es True significa que ya se inscribieron con esa CI
            ciBoolean = True
            try:
                f = InscripcionBase.objects.get(actividad=actividad, cedula=cedula)
            except ObjectDoesNotExist:
                ciBoolean = False

            if ciBoolean:
                mensaje = u'Ya existe una inscripción con la cédula ' + cedula + u' en la actividad ' + actividad.nombre
                messages.error(request, mensaje)
                return HttpResponseRedirect(reverse('inicio'))

            inscripto = form.save()

            m, txt = encode_data(str(inscripto.id))
            print(m)
            print(txt)
            url_info = request.scheme + '://' + request.META['HTTP_HOST'] + '/inscripto?m=' + urllib.parse.quote(m) + '&text=' + urllib.parse.quote(txt)
            enviar_mail_inscripcion(inscripto, url_info)
            return HttpResponseRedirect(url_info)
    else:
        form = InscripcionBaseForm()

    print(request.META['HTTP_HOST'])
    print(request.scheme)
    context = {
        'form': form,
        'nombre_actividad': actividad.nombre,

    }

    return render(request, 'form.html', context)


def inscripcion_extra(request):
    m = request.GET.get('m')
    text = request.GET.get('text')
    try:
        idInscripto = decode_data(m, text)
    except:
        messages.error(request, u'La url no es correcta.')
        return HttpResponseRedirect(reverse('inicio'))

    inscripto = get_object_or_404(InscripcionBase, pk=idInscripto)

    if inscripto.datos is not None:
        messages.error(request, u'Ya ha completado los datos extras.')
        return HttpResponseRedirect(reverse('inicio'))

    form_entry = inscripto.actividad.formDinamico

    form_element_entries = form_entry.formelemententry_set.all()[:]
    print(form_element_entries)
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

            mensaje = u'Su solicitud ha sido procesada con éxito. Gracias por inscribirse'
            messages.success(request, mensaje)
            return HttpResponseRedirect(reverse('inicio'))
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
        'inscripto': inscripto,
    }

    return render(request, 'formextra.html', context)


from django.conf import settings
from django.template import Template, Context

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import base64
import smtplib

def get_oauth2_token():
    creds = Credentials(
        None,
        refresh_token=settings.EMAIL_OAUTH2_REFRESH_TOKEN,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=settings.EMAIL_OAUTH2_CLIENT_ID,
        client_secret=settings.EMAIL_OAUTH2_CLIENT_SECRET,
    )
    creds.refresh(Request()) 
    return creds.token

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_email, body, subject):
    access_token = get_oauth2_token()
    
    auth_string = f"user={settings.EMAIL_HOST_USER}\1auth=Bearer {access_token}\1\1"
    auth_encoded = base64.b64encode(auth_string.encode()).decode()

    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    server.starttls()
    server.ehlo()
    server.docmd("AUTH", "XOAUTH2 " + auth_encoded)

    msg = MIMEMultipart()
    msg["From"] = settings.EMAIL_HOST_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html", "utf-8"))

    server.sendmail(settings.EMAIL_HOST_USER, to_email, msg.as_string())  
    server.quit()


@lru_cache(maxsize=2)
def get_mail_template(is_titular):
    """Cache mail templates to avoid repeated database queries."""
    key = settings.MAIL_TITULAR_KEY if is_titular else settings.MAIL_SUPLENTE_KEY
    return Parametro.objects.get(clave=key).valor

def enviar_mail_inscripcion(inscripcion_guardada, url_info):
    """Prepara y envia el mail para una inscripción realizada."""
    actividad = inscripcion_guardada.actividad
    is_titular = inscripcion_guardada.puesto <= actividad.cantidadTitulares
    
    template_valor = get_mail_template(is_titular)
    template = Template(template_valor)
    
    context = Context({
        'inscripto': inscripcion_guardada,
        'contactoTitular': actividad.emailContacto,
        'mail_url' if is_titular else 'url_info': url_info
    })

    html_render = template.render(context)
    send_email(inscripcion_guardada.mail, html_render, actividad.nombre)



import hashlib, zlib
import pickle
import urllib

@lru_cache(maxsize=1)
def get_secret_hash():
    """Cache the secret hash value to avoid repeated database queries."""
    return Parametro.objects.get(clave=settings.SECRET_HASH_KEY).valor

def encode_data(data):
    """Turn `data` into a hash and an encoded string, suitable for use with `decode_data`."""
    secret_value = get_secret_hash()
    
    compressed_data = zlib.compress(pickle.dumps(data, 0))
    encoded_data = base64.b64encode(compressed_data).decode('utf-8')

    m = hashlib.md5((secret_value + encoded_data).encode('utf-8')).hexdigest()[:12] 

    return m, encoded_data

def decode_data(hash, text):
    """Turn a hash and encoded string (generated by `encode_data`) back into the original data."""
    secret_value = get_secret_hash()
    
    # URL-decode both parameters since they were URL-encoded when generating the URL
    hash = urllib.parse.unquote(hash)
    text = urllib.parse.unquote(text)
    
    m = hashlib.md5((secret_value + text).encode('utf-8')).hexdigest()[:12] 

    if m != hash:
        raise Exception(f"Bad hash! Expected {m} but got {hash}")

    decoded_data = base64.b64decode(text)
    data = pickle.loads(zlib.decompress(decoded_data)) 

    return data

from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView


class ActividadList(ListView):
    #Muestra las actividades que se van a habilitar en 7 dias o menos
    fechaApertura = timezone.now() + timedelta(days=8)
    # Muestra las actividades que no finalizaron aun
    fechafin = timezone.now() - timedelta(days=1)
    actividades = Actividad.objects.filter(fechaCierre__gte=timezone.now()).order_by("tipo_id", "-fechaApertura")
    actividades = actividades.filter(fechaFin__gte=fechafin).filter(fechaApertura__lte=fechaApertura)
    queryset = actividades
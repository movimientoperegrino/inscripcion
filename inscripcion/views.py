# -*- coding: utf-8 -*-

from django.shortcuts import render

# Create your views here.
import datetime
from datetime import timedelta
from django.utils import timezone
from models import *
from forms import *
import logging

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

from fobi.settings import GET_PARAM_INITIAL_DATA, DEBUG
import csv
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm



logger = logging.getLogger(__name__)

def info_inscripto(request):
    m = request.GET.get('m')
    text = request.GET.get('text')
    inscripto_id = decode_data(m, text)
    inscripto = InscripcionBase.objects.get(id=inscripto_id)
    form = InscriptoInfo(instance=inscripto)
    context = {'form': form}
    return render_to_response('form.html', context,
                              context_instance=RequestContext(request))



def iniciar_sesion(request):
    mensaje =""
    if not request.user.is_anonymous():
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
    return render_to_response('admin/login.html', {'form': form, 'mensaje': mensaje},
                              context_instance=RequestContext(request))

def cerrar_sesion(request):
    logout(request)
    return HttpResponseRedirect('/login')

@login_required(login_url='/login')
def lista_actividades(request):
    actividades = Actividad.objects.all().order_by('-fechaApertura')
    for a in actividades:
        print a.fechaApertura
    return render_to_response(
        'admin/actividad_list.html',
        {'lista_actividades': actividades},
        context_instance=RequestContext(request)
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
    return render_to_response(
        'admin/form.html',
        {'form': form, 'titulo': titulo},
        context_instance=RequestContext(request)
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
    return render_to_response(
        'admin/form.html',
        {'form': form, 'titulo': titulo},
        context_instance=RequestContext(request)
    )

@login_required(login_url='/login')
def eliminar_actividad(request, id_actividad):
    try:
        actividad = Actividad.objects.get(pk=id_actividad)
    except Actividad.DoesNotExist:
        raise Http404
    return render_to_response(
        'admin/eliminar_actividad.html',
        {'actividad': actividad},
        context_instance=RequestContext(request)
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
    return render_to_response(
        'admin/actividad_list.html',
        {'mensaje': mensaje, 'lista_actividades': actividades},
        context_instance=RequestContext(request)
    )


@login_required(login_url='/login')
def url_inscripcion_extra(request, id_inscripto):
    m, txt = encode_data(str(id_inscripto))
    #url_info = request.scheme + '://' + request.META['HTTP_HOST'] + '/inscripto?m="' + m + '"&text="' + txt +'"'
    url_info = request.scheme + '://' + request.META['HTTP_HOST'] + '/inscripto?m=' + urllib.quote(m) + '&text=' + urllib.quote(txt)
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
    m, txt = encode_data(actividad.id)


    url_contacto = request.scheme + '://' + request.META['HTTP_HOST'] + '/inscriptos?m=' + m + '&text=' + txt
    url_csv = request.scheme + '://' + request.META['HTTP_HOST'] + '/csv?m=' + m + '&text=' + txt
    context = {'lista_inscriptos': lista_inscriptos,
               'actividad': actividad,
               'cabecera': cabecera,
               'jsontitles': jsontitles,
               'url_contacto': url_contacto,
               'url_csv': url_csv,
               }
    return render_to_response('admin/inscriptos.html', context,
                              context_instance=RequestContext(request))


def lista_inscriptos(request):
    m = request.GET.get('m')
    text = request.GET.get('text')
    try:
        actividad_id = decode_data(m, text)
    except:
        mensaje = u'La url no es correcta.'
        return render_to_response(
            'error.html',
            {'mensaje': mensaje},
            context_instance=RequestContext(request)
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

    url_csv = request.scheme + '://' + request.META['HTTP_HOST'] + '/csv?m=' + m + '&text=' + text
    context = {'lista_inscriptos': lista_inscriptos,
               'actividad': actividad,
               'cabecera': cabecera,
               'jsontitles': jsontitles,
               'url_csv': url_csv,
               }
    return render_to_response('inscriptos.html', context,
                              context_instance=RequestContext(request))


def descargar_csv(request):
    m = request.GET.get('m')
    text = request.GET.get('text')
    try:
        actividad_id = decode_data(m, text)
    except:
        mensaje = u'La url no es correcta.'
        return render_to_response(
            'error.html',
            {'mensaje': mensaje},
            context_instance=RequestContext(request)
        )
    actividad = get_object_or_404(Actividad, pk=actividad_id)
    # print actividad
    # m, txt = encode_data(idActividad)
    # print m
    # print txt
    # url_info = request.scheme + '://' + request.META['HTTP_HOST'] + '/inscriptos?m=' + m + '&text=' + txt
    # return HttpResponseRedirect(url_info)
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

    print request.get_full_path()
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

            m, txt = encode_data(inscripto.id)
            print m
            print txt
            url_info = request.scheme + '://' + request.META['HTTP_HOST'] + '/inscripto?m=' + urllib.quote(m) + '&text=' + urllib.quote(txt)
            enviar_mail_inscripcion(inscripto, url_info)
            return HttpResponseRedirect(url_info)
    else:
        form = InscripcionBaseForm()

    print request.META['HTTP_HOST']
    print request.scheme
    context = {
        'form': form,
    }

    return render_to_response('form.html', context,
                              context_instance=RequestContext(request))


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

    return render_to_response('formextra.html', context,
                              context_instance=RequestContext(request))


from django.conf import settings
from django.template import Template, Context


def envio_mail(destino, cuerpo, asunto, adjunto=None):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    from django.core.mail import EmailMultiAlternatives

    origen = '[Movimiento Peregrino] <retiros-noreply@movimientoperegrino.org>'
    destino = 'informatica@movimientoperegrino.org' if settings.DESARROLLO else destino

    try:
        #validate_email(destino)
        msg = EmailMultiAlternatives(asunto, cuerpo, origen, [destino])
        msg.attach_alternative(cuerpo, 'text/html')
        msg.send()
    except ValidationError:
        print "Error en el envio de mail"

def enviar_mail_inscripcion(inscripcion_guardada, url_info):
   """ Prepara y envia el mail para una inscripción realizada.
   """

   actividad = inscripcion_guardada.actividad

   template = None
   html_render = None
   context = None
   if inscripcion_guardada.puesto <= actividad.cantidadTitulares: #inscripcion_guardada.posicion <= actividad.cantidad_titulares:
       context = Context(
           {'inscripto': inscripcion_guardada, 'contactoTitular': inscripcion_guardada.actividad.emailContacto,'mail_url': url_info})
       parametro = Parametro.objects.get(clave=settings.MAIL_TITULAR_KEY)
       template = Template(parametro.valor)
   else:
       context = Context(
           {'inscripto': inscripcion_guardada, 'contactoTitular': inscripcion_guardada.actividad.emailContacto,
           'url_info': url_info})
       parametro = Parametro.objects.get(clave=settings.MAIL_SUPLENTE_KEY)
       template = Template(parametro.valor)

   html_render = template.render(context)
   envio_mail(inscripcion_guardada.mail, html_render, inscripcion_guardada.actividad.nombre)



import hashlib, zlib
import cPickle as pickle
import urllib


def encode_data(data):
    my_secret = Parametro.objects.get(clave=settings.SECRET_HASH_KEY)
    """Turn `data` into a hash and an encoded string, suitable for use with `decode_data`."""
    text = zlib.compress(pickle.dumps(data, 0)).encode('base64').replace('\n', '')
    m = hashlib.md5(my_secret.valor + text).hexdigest()[:12]

    return m, text

def decode_data(hash, enc):
    my_secret = Parametro.objects.get(clave=settings.SECRET_HASH_KEY)
    """The inverse of `encode_data`."""
    text = urllib.unquote(enc)
    m = hashlib.md5(my_secret.valor + text).hexdigest()[:12]
    if m != hash:
        raise Exception("Bad hash!")
    data = pickle.loads(zlib.decompress(text.decode('base64')))

    return data

    #print decode_data(hash, enc)

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
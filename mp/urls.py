"""mp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from inscripcion import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    # View URLs
    url(r'^fobi/', include('fobi.urls.view')),

    # Edit URLs
    url(r'^fobi/', include('fobi.urls.edit')),

     #DB Store plugin URLs
    url(r'^fobi/plugins/form-handlers/db-store/',
        include('fobi.contrib.plugins.form_handlers.db_store.urls')),

    # View form entry
    url(r'^view/(?P<form_entry_slug>[\w_\-]+)/$',
        'fobi.views.view_form_entry',
        name='fobi.view_form_entry'),

    url(r'^$', views.ActividadList.as_view(), name='inicio'),

    url(r'^form/(?P<form_entry_slug>[\w_\-]+)/$', 'inscripcion.views.form'),

    url(r'^actividad/(?P<idActividad>\d+)/$', 'inscripcion.views.inscripcion_actividad'),
    url(r'^lista/(?P<idActividad>\d+)/$', 'inscripcion.views.inscriptos_actividad'),
    url(r'^csv/$', 'inscripcion.views.descargar_csv'),
    url(r'^inscripto/$', 'inscripcion.views.inscripcion_extra'),
    url(r'^inscriptos/$', 'inscripcion.views.lista_inscriptos'),
    url(r'^actividades/$', 'inscripcion.views.lista_actividades'),
    url(r'^actividades/nueva$', 'inscripcion.views.nueva_actividad'),
    url(r'^actividades/(?P<id_actividad>\d+)/editar/$', 'inscripcion.views.editar_actividad'),
    url(r'^actividades/(?P<id_actividad>\d+)/eliminar/$', 'inscripcion.views.eliminar_actividad'),
    url(r'^actividades/(?P<id_actividad>\d+)/eliminada/$', 'inscripcion.views.actividad_eliminada'),
    url(r'^logout/$', 'inscripcion.views.cerrar_sesion'),
    url(r'^login/$', 'inscripcion.views.iniciar_sesion'),
    url(r'^urlinscripto/(?P<id_inscripto>\d+)/$', 'inscripcion.views.url_inscripcion_extra'),

]

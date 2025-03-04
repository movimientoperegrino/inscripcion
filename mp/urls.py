"""mp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.urls import include, re_path
from django.contrib import admin
from inscripcion import views as inscripcion_views
from fobi.views import view_form_entry

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),

    # View URLs from django-fobi
    re_path(r'^fobi/', include('fobi.urls.view')),

    # Edit URLs from django-fobi
    re_path(r'^fobi/', include('fobi.urls.edit')),

    # DB Store plugin URLs
    re_path(r'^fobi/plugins/form-handlers/db-store/', include('fobi.contrib.plugins.form_handlers.db_store.urls')),

    # View form entry (converted from string to callable)
    re_path(r'^view/(?P<form_entry_slug>[\w_\-]+)/$', view_form_entry, name='fobi.view_form_entry'),

    # Custom application URLs (using callables instead of string references)
    re_path(r'^$', inscripcion_views.ActividadList.as_view(), name='inicio'),
    re_path(r'^form/(?P<form_entry_slug>[\w_\-]+)/$', inscripcion_views.form, name='form'),
    re_path(r'^actividad/(?P<idActividad>\d+)/$', inscripcion_views.inscripcion_actividad, name='actividad'),
    re_path(r'^lista/(?P<idActividad>\d+)/$', inscripcion_views.inscriptos_actividad, name='lista'),
    re_path(r'^csv/$', inscripcion_views.descargar_csv, name='csv'),
    re_path(r'^inscripto/$', inscripcion_views.inscripcion_extra, name='inscripto'),
    re_path(r'^inscriptos/$', inscripcion_views.lista_inscriptos, name='inscriptos'),
    re_path(r'^actividades/$', inscripcion_views.lista_actividades, name='actividades'),
    re_path(r'^actividades/nueva$', inscripcion_views.nueva_actividad, name='nueva_actividad'),
    re_path(r'^actividades/(?P<id_actividad>\d+)/editar/$', inscripcion_views.editar_actividad, name='editar_actividad'),
    re_path(r'^actividades/(?P<id_actividad>\d+)/eliminar/$', inscripcion_views.eliminar_actividad, name='eliminar_actividad'),
    re_path(r'^actividades/(?P<id_actividad>\d+)/eliminada/$', inscripcion_views.actividad_eliminada, name='actividad_eliminada'),
    re_path(r'^logout/$', inscripcion_views.cerrar_sesion, name='logout'),
    re_path(r'^login/$', inscripcion_views.iniciar_sesion, name='login'),
    re_path(r'^urlinscripto/(?P<id_inscripto>\d+)/$', inscripcion_views.url_inscripcion_extra, name='urlinscripto'),
]

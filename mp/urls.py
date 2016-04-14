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
        'inscripcion.views.view_form_entry',
        name='fobi.view_form_entry'),

    url(r'^form/(?P<form_entry_slug>[\w_\-]+)/$', 'inscripcion.views.form'),

    url(r'^actividad/(?P<idActividad>\d+)/$', 'inscripcion.views.inscripcion_actividad'),
    url(r'^inscripto/(?P<idInscripto>\d+)/$', 'inscripcion.views.inscripcion_extra'),
    url(r'^info/(?P<idInscripto>\d+)/$', 'inscripcion.views.info_inscripto'),
    url(r'^info2/$', 'inscripcion.views.info_inscripto'),
]

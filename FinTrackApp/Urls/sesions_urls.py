from django.urls import path

from FinTrackApp.Apis.Sesiones.SesionesApi import *
urlpatterns = [
    path('LoginUsuario/',LoginUsuario.as_view(),name="LoginUsuario"), 
    path('ComprobarSession/',ComprobarSession.as_view(),name="LoginUsuario"), 
    
    
]
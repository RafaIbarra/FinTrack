from django.urls import path
from FinTrackApp.Apis.Operaciones.InformesResumen import *

urlpatterns= [
        path('ResumenOperacionesMes/<int:anno>/<int:mes>/',ResumenOperacionesMes.as_view(),name="ResumenOperacionesMes"), 
]
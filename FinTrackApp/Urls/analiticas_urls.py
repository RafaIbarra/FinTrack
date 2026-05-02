from django.urls import path
from FinTrackApp.Apis.Analitica.InformesApi import *
from FinTrackApp.Apis.Analitica.EstadistasApi import *

urlpatterns_informes= [
        path('ResumenMovimientoMes/<int:anno>/<int:mes>/',ResumenMovimientoMes.as_view(),name="ResumenMovimientoMes"), 
]
urlpatterns_estadisticas= [
        path('EstadisticaMes/<int:anno>/<int:mes>/',EstadisticaMes.as_view(),name="EstadisticaMes"), 
]

urlpatterns=urlpatterns_informes + urlpatterns_estadisticas
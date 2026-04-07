from django.urls import path
from FinTrackApp.Apis.IA.IAConsultasApi import *
urlpatterns =[
    path('ConsultaGastosUser/',ConsultaGastosUser.as_view(),name="ConsultaGastosUser"), 
]
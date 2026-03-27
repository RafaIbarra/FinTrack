from django.urls import path
from FinTrackApp.Apis.Admin.UsuariosApi import *
urlpatterns = [
    path('RegistroUsuario/',RegistroUsuario.as_view(),name="RegistroUsuario"), 
    
    
]
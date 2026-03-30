from django.urls import path


from FinTrackApp.Apis.Referenciales.CategoriaGastoApi import *
from FinTrackApp.Apis.Referenciales.GastosApi import *
urlpatterns = [
    path('CategoriaGastoUsuarioApi/',CategoriaGastoUsuarioApi.as_view(),name="CategoriaGastoUsuarioApi"), 
    path('CategoriaGastoUsuarioApi/<int:id_reg>/',CategoriaGastoUsuarioApi.as_view(),name="CategoriaGastoUsuarioApi"),     
    path('ListadoCageriasUser/',ListadoCageriasUser.as_view(),name="ListadoCageriasUser"),     
    path('OperacionesGastosUsuario/',OperacionesGastosUsuario.as_view(),name="OperacionesGastosUsuario"), 
    path('ListarGastosUser/',ListarGastosUser.as_view(),name="ListarGastosUser"), 
    
    
]

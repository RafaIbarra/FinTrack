from django.urls import path


from FinTrackApp.Apis.Referenciales.CategoriaGastoApi import *
from FinTrackApp.Apis.Referenciales.GastosApi import *
from FinTrackApp.Apis.Referenciales.MediosPagosApi import *
from FinTrackApp.Apis.Referenciales.IngresosApi import *
urlpatterns = [
    path('CategoriaGastoUsuarioApi/',CategoriaGastoUsuarioApi.as_view(),name="CategoriaGastoUsuarioApi"), 
    path('CategoriaGastoUsuarioApi/<int:id_reg>/',CategoriaGastoUsuarioApi.as_view(),name="CategoriaGastoUsuarioApi"),     
    path('ListadoCageriasUser/',ListadoCageriasUser.as_view(),name="ListadoCageriasUser"),     
    path('OperacionesGastosUsuario/',OperacionesGastosUsuario.as_view(),name="OperacionesGastosUsuario"), 
    path('OperacionesGastosUsuario/<int:idgasto>/',OperacionesGastosUsuario.as_view(),name="OperacionesGastosUsuario"), 
    path('ListarGastosUser/',ListarGastosUser.as_view(),name="ListarGastosUser"), 

    path('OperacionesMediosPagosUsuario/',OperacionesMediosPagosUsuario.as_view(),name="OperacionesMediosPagosUsuario"), 
    path('OperacionesMediosPagosUsuario/<int:idmedio>/',OperacionesMediosPagosUsuario.as_view(),name="OperacionesMediosPagosUsuario"),     
    path('ListadoMedioPagosUser/',ListadoMedioPagosUser.as_view(),name="ListadoMedioPagosUser"), 

    path('OperacionesIngresoUsuario/',OperacionesIngresoUsuario.as_view(),name="OperacionesIngresoUsuario"), 
    path('OperacionesIngresoUsuario/<int:idingreso>/',OperacionesIngresoUsuario.as_view(),name="OperacionesIngresoUsuario"),     
    path('ListarIngresosUser/',ListarIngresosUser.as_view(),name="ListarIngresosUser"), 
    
    
]

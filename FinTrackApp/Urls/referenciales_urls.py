from django.urls import path


from FinTrackApp.Apis.Referenciales.CategoriaGastoApi import *
from FinTrackApp.Apis.Referenciales.GastosApi import *
from FinTrackApp.Apis.Referenciales.MediosPagosApi import *
from FinTrackApp.Apis.Referenciales.IngresosApi import *
from FinTrackApp.Apis.Referenciales.EmpresasApi import *
urlpatterns = [
    path('OperacionesCategoriasGastosUser/',OperacionesCategoriasGastosUser.as_view(),name="OperacionesCategoriasGastosUser"), 
    path('OperacionesCategoriasGastosUser/<int:id_reg>/',OperacionesCategoriasGastosUser.as_view(),name="OperacionesCategoriasGastosUser"),     
    path('ListadoCategoriasUser/',ListadoCategoriasUser.as_view(),name="ListadoCategoriasUser"),     
    path('OperacionesGastosUser/',OperacionesGastosUser.as_view(),name="OperacionesGastosUser"), 
    path('OperacionesGastosUser/<int:idgasto>/',OperacionesGastosUser.as_view(),name="OperacionesGastosUser"), 
    path('ListarGastosUser/',ListarGastosUser.as_view(),name="ListarGastosUser"), 

    path('OperacionesMediosPagosUser/',OperacionesMediosPagosUser.as_view(),name="v"), 
    path('OperacionesMediosPagosUser/<int:idmedio>/',OperacionesMediosPagosUser.as_view(),name="OperacionesMediosPagosUser"),     
    path('ListadoMedioPagosUser/',ListadoMedioPagosUser.as_view(),name="ListadoMedioPagosUser"), 

    path('OperacionesIngresoUser/',OperacionesIngresoUser.as_view(),name="OperacionesIngresoUser"), 
    path('OperacionesIngresoUser/<int:idingreso>/',OperacionesIngresoUser.as_view(),name="OperacionesIngresoUser"),     
    path('ListarIngresosUser/',ListarIngresosUser.as_view(),name="ListarIngresosUser"), 


    path('ListadoEmpresas/<int:id_empresa>/',ListadoEmpresas.as_view(),name="ListadoEmpresas"),
    path('OperacionesEmpresas/',OperacionesEmpresas.as_view(),name="OperacionesEmpresas"),     
    path('OperacionesEmpresas/<int:id_empresa>/',OperacionesEmpresas.as_view(),name="OperacionesEmpresas"),
    
    
]

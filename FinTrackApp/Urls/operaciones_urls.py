from django.urls import path


from FinTrackApp.Apis.Operaciones.MovimientosGastosApi import *
from FinTrackApp.Apis.Operaciones.ListadoMovimientosGastosApi import *

from FinTrackApp.Apis.Operaciones.MovimientosIngresosApi import *
from FinTrackApp.Apis.Operaciones.ListadoMovimientosIngresosApi import *

url_registros=[
    path('RegistroMovimientoGastoUser/',RegistroMovimientoGastoUser.as_view(),name="RegistroMovimientoGastoUser"), 
    path('EliminarMovimientoGastoUser/<int:idmovimiento>/',EliminarMovimientoGastoUser.as_view(),name="EliminarMovimientoGastoUser"), 
    path('EditarMovimientoGastoUser/<int:idmovimiento>/',EditarMovimientoGastoUser.as_view(),name="EditarMovimientoGastoUser"),

    path('RegistroMovimientoIngresoUser/',RegistroMovimientoIngresoUser.as_view(),name="RegistroMovimientoIngresoUser"), 
    path('EditarMovimientoIngresoUser/<int:idmovimiento>/',EditarMovimientoIngresoUser.as_view(),name="EditarMovimientoIngresoUser"),
    path('EliminarMovimientoIngresoUser/<int:idmovimiento>/',EliminarMovimientoIngresoUser.as_view(),name="EliminarMovimientoIngresoUser"), 

    
]
url_listados= [
    path('ListadoMovimientoGastosUser/',ListadoMovimientoGastosUser.as_view(),name="ListadoMovimientoGastosUser"), 
    path('ListadoMovimientosIngresosUser/',ListadoMovimientosIngresosUser.as_view(),name="ListadoMovimientosIngresosUser"), 
    path('ListadoDetalleGastosUser/',ListadoDetalleGastosUser.as_view(),name="ListadoDetalleGastosUser"), 
    
    ]


urlpatterns = url_registros + url_listados
     
    
  
    

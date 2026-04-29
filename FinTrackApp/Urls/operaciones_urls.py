from django.urls import path


from FinTrackApp.Apis.Operaciones.MovimientosGastosApi import *
from FinTrackApp.Apis.Operaciones.ListadoMovimientosGastosApi import *

from FinTrackApp.Apis.Operaciones.MovimientosIngresosApi import *
from FinTrackApp.Apis.Operaciones.ListadoMovimientosIngresosApi import *

url_registros_mov_gastos=[
    path('RegistroMovimientoGastoUser/',RegistroMovimientoGastoUser.as_view(),name="RegistroMovimientoGastoUser"), 
    path('EliminarMovimientoGastoUser/<int:idmovimiento>/',EliminarMovimientoGastoUser.as_view(),name="EliminarMovimientoGastoUser"), 
    path('EditarMovimientoGastoUser/<int:idmovimiento>/',EditarMovimientoGastoUser.as_view(),name="EditarMovimientoGastoUser"),
]
url_listados_mov_gastos= [
    path('ListadoMovimientoGastosUser/',ListadoMovimientoGastosUser.as_view(),name="ListadoMovimientoGastosUser"), 
    path('ListadoMovimientoGastosMesUser/<int:anno>/<int:mes>/',ListadoMovimientoGastosMesUser.as_view(),name="ListadoMovimientoGastosUser"), 
    path('DatosReferencialesCargosMovimiento/<int:id>/',DatosReferencialesCargosMovimiento.as_view(),name="DatosReferencialesCargosMovimiento"), 
    path('ListadoDetalleGastosUser/',ListadoDetalleGastosUser.as_view(),name="ListadoDetalleGastosUser"), 
    path('ReferencialesCargaGasto/',ReferencialesCargaGasto.as_view(),name="ReferencialesCargaGasto"), 
    
    ]


url_registros_mov_ingresos=[
    path('RegistroMovimientoIngresoUser/',RegistroMovimientoIngresoUser.as_view(),name="RegistroMovimientoIngresoUser"), 
    path('EditarMovimientoIngresoUser/<int:idmovimiento>/',EditarMovimientoIngresoUser.as_view(),name="EditarMovimientoIngresoUser"),
    path('EliminarMovimientoIngresoUser/<int:idmovimiento>/',EliminarMovimientoIngresoUser.as_view(),name="EliminarMovimientoIngresoUser"),
]

url_listados_mov_ingresos= [
    
    path('ListadoMovimientosIngresosUser/',ListadoMovimientosIngresosUser.as_view(),name="ListadoMovimientosIngresosUser"), 
    path('ListadoMovimientosIngresosMesUser/<int:anno>/<int:mes>/',ListadoMovimientosIngresosMesUser.as_view(),name="ListadoMovimientoGastosUser"), 
    ]

urlpatterns = url_registros_mov_gastos + url_listados_mov_gastos + url_registros_mov_ingresos +url_listados_mov_ingresos
     
    
  
    

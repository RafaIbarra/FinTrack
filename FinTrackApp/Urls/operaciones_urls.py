from django.urls import path


from FinTrackApp.Apis.Operaciones.MovimientosGastosApi import *
from FinTrackApp.Apis.Operaciones.ListadoMovimientosGastosApi import *
urlpatterns = [
    path('RegistroMovimientoGastoUser/',RegistroMovimientoGastoUser.as_view(),name="RegistroMovimientoGastoUser"), 
    path('EliminarMovimientoGastoUser/<int:idmovimiento>/',EliminarMovimientoGastoUser.as_view(),name="EliminarMovimientoGastoUser"), 
    path('EditarMovimientoGastoUser/<int:idmovimiento>/',EditarMovimientoGastoUser.as_view(),name="EditarMovimientoGastoUser"), 
    path('ListadoMovimientoGastosUser/',ListadoMovimientoGastosUser.as_view(),name="ListadoMovimientoGastosUser"), 
  
    
    
]

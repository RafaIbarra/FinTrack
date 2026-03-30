from django.urls import path


from FinTrackApp.Apis.Referenciales.CategoriaGastoApi import *
urlpatterns = [
    path('CategoriaGastoUsuarioApi/',CategoriaGastoUsuarioApi.as_view(),name="CategoriaGastoUsuarioApi"), 
    path('CategoriaGastoUsuarioApi/<int:id_reg>/',CategoriaGastoUsuarioApi.as_view(),name="CategoriaGastoUsuarioApi"),     
    path('ListadoCageriasUser/',ListadoCageriasUser.as_view(),name="ListadoCageriasUser"),     
    
]

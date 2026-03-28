from django.urls import path


from FinTrackApp.Apis.Referenciales.CategoriaGastoApi import *
urlpatterns = [
    path('RegistroCategoria/',RegistroCategoria.as_view(),name="RegistroCategoria"), 
    
    
]
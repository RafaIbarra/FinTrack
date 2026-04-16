import os
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db import transaction

from FinTrackApp.Decoradores.DecoradoresSeguridad import AutenticacionToken
from FinTrackApp.Modelos.Empresas import Empresas
from FinTrackApp.Serializadores.SerilizadoresModelos.EmpresasSerializers import *

class ListadoEmpresas(APIView):
    @AutenticacionToken
    def get(self, request, id_empresa=0, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info.get("username")
            id_usuario = user_info.get('usuario_id')
            
            # Mejorar la lógica de consulta
            if id_empresa == 0:
                # Obtener todas las empresas (con optimización si hay relaciones)
                empresas = Empresas.objects.all()
                
                if not empresas.exists():
                    return Response(
                        {'message': 'No hay empresas cargadas.', 'data': []},
                        status=status.HTTP_200_OK
                    )
                
                serializer = InfoEmpresasSerializer(empresas, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            else:
                # Obtener una empresa específica
                try:
                    empresa = Empresas.objects.get(Id=id_empresa)
                    serializer = InfoEmpresasSerializer(empresa)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except Empresas.DoesNotExist:
                    return Response(
                        {'message': f'No existe una empresa con ID {id_empresa}'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
        except Exception as e:
            return Response(
                {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OperacionesEmpresas(APIView):

    @AutenticacionToken
    def post(self, request, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario = user_info.get('usuario_id')

            nombre_empresa = request.data.get('nombre', '').strip()
            ruc = request.data.get('ruc', '')
            
            # El logo es opcional - puede ser None
            imagen_file = request.FILES.get('logo')  # Puede ser None
            
            # Preparar datos para el serializer
            data_registrar = {
                'NombreEmpresa': nombre_empresa,
                'Ruc': ruc,
            }
            
            # Solo agregar UrlImg si se envió un archivo
            if imagen_file:
                data_registrar['UrlImg'] = imagen_file
            
            # ObsImg puede ser opcional o null
            
            
            
            serializer = RegistroEmpresaSerializer(data=data_registrar)
            
            if not serializer.is_valid():
                # Concatenar errores
                mensajes_error = []
                for campo, mensajes in serializer.errors.items():
                    for mensaje in mensajes:
                        mensajes_error.append(f"{campo}: {mensaje}")
                
                error_concatenado = "; ".join(mensajes_error)
                
                return Response({
                    'message': error_concatenado,
                    'detalles': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # ✅ IMPORTANTE: llamar al método save()
            empresa_save = serializer.save()
            
            # Serializar para respuesta
            detail_serializer = InfoEmpresasSerializer(empresa_save)
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
          
        except Exception as e:
            return Response(
                {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @AutenticacionToken
    def put(self, request, id_empresa, *args, **kwargs):
        try:
            try:
                id_empresa = int(id_empresa)
            except (TypeError, ValueError):
                return Response(
                    {'message': 'El ID de empresa debe ser un número válido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            empresa=Empresas.objects.filter(Id=id_empresa)
            if not empresa.exists():
                return Response({'message': f'No existe una empresa con ID {id_empresa}'}, status=status.HTTP_404_NOT_FOUND)
            
            nombre_empresa = request.data.get('nombre', '').strip()
            ruc = request.data.get('ruc', '')
            nuevo_logo = request.FILES.get('logo')
            
            instancia_empresa=empresa.first()
            
            with transaction.atomic():
                # Eliminar logo anterior SOLO si se envía nuevo logo
                if nuevo_logo and instancia_empresa.UrlImg:
                    try:
                        if instancia_empresa.UrlImg.path and os.path.isfile(instancia_empresa.UrlImg.path):
                            os.remove(instancia_empresa.UrlImg.path)
                    except OSError as e:
                        # Si no se puede eliminar, continuar igual (el logo se reemplazará)
                        print(f"Advertencia: No se pudo eliminar {instancia_empresa.UrlImg.path}: {e}")
                
                # Construir datos a actualizar
                instancia_empresa=empresa.first()
                data_actualizar = {
                'NombreEmpresa': nombre_empresa,
                'Ruc': ruc,
                }
                
                if nuevo_logo:
                    data_actualizar['UrlImg'] = nuevo_logo
                
                serializer = RegistroEmpresaSerializer(instance=instancia_empresa,data=data_actualizar)
                if not serializer.is_valid():
                    # Obtener todos los mensajes de error
                    errores = serializer.errors
                    
                    # Concatenar todos los mensajes en un solo string
                    mensajes_error = []
                    
                    for campo, mensajes in errores.items():
                        # Cada campo puede tener una lista de mensajes
                        for mensaje in mensajes:
                            # Agregar el campo al mensaje
                            mensajes_error.append(f"{campo}: {mensaje}")
                    
                    # Unir todos los mensajes con punto y coma
                    error_concatenado = "; ".join(mensajes_error)
                    
                    return Response({
                        'message': error_concatenado,
                        'detalles': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                empresa_save = serializer.save()
                detail_serializer = InfoEmpresasSerializer(empresa_save)
                return Response(detail_serializer.data, status=status.HTTP_200_OK)
          
        except Exception as e:
            return Response(
                {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    
    @AutenticacionToken
    def delete(self, request, id_empresa, *args, **kwargs):
        try:
            # Verificar que id_empresa sea válido
            try:
                id_empresa = int(id_empresa)
            except (TypeError, ValueError):
                return Response(
                    {'message': 'El ID de empresa debe ser un número válido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            
            empresa_reg=Empresas.objects.filter(Id=id_empresa)
            if not empresa_reg.exists():
                return Response(
                    {'message': f'No existe una empresa con Id={id_empresa}.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            instancia_empresa=empresa_reg.first()
            
            # Guardar la ruta del logo antes de eliminar
            logo_path = None
            if instancia_empresa.UrlImg and instancia_empresa.UrlImg.path:
                logo_path = instancia_empresa.UrlImg.path
            
            # Iniciar transacción atómica
            with transaction.atomic():
                # Primero eliminar el registro de la base de datos
                instancia_empresa.delete()
                
                # Luego eliminar el archivo del logo (si existe)
                if logo_path and os.path.isfile(logo_path):
                    os.remove(logo_path)
            
            return Response({
                'message': f'Empresa con ID {id_empresa} eliminada exitosamente'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
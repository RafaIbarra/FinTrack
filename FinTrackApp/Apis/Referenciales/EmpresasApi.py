import os
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db import transaction

from FinTrackApp.Decoradores.DecoradoresSeguridad import AutenticacionToken
from FinTrackApp.Modelos.Empresas import Empresas
from FinTrackApp.Serializadores.SerilizadoresModelos.EmpresasSerializers import *
from FinTrackApp.Utils.r2_storage import r2_storage


class ListadoEmpresas(APIView):
    @AutenticacionToken
    def get(self, request, id_empresa=0, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info.get("username")
            id_usuario = user_info.get('usuario_id')

            if id_empresa == 0:
                empresas = Empresas.objects.all()

                if not empresas.exists():
                    return Response(
                        {'message': 'No hay empresas cargadas.', 'data': []},
                        status=status.HTTP_200_OK
                    )

                serializer = InfoEmpresasSerializer(empresas, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            else:
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
            imagen_file = request.FILES.get('logo')

            # Preparar datos para el serializer (sin logo, eso se maneja aparte)
            data_registrar = {
                'NombreEmpresa': nombre_empresa,
                'Ruc': ruc,
            }

            serializer = RegistroEmpresaSerializer(data=data_registrar)

            if not serializer.is_valid():
                mensajes_error = []
                for campo, mensajes in serializer.errors.items():
                    for mensaje in mensajes:
                        mensajes_error.append(f"{campo}: {mensaje}")

                error_concatenado = "; ".join(mensajes_error)

                return Response({
                    'message': error_concatenado,
                    'detalles': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            # Guardar empresa en DB (sin logo por ahora)
            empresa_save = serializer.save()

            # Si hay logo, subir a R2 y actualizar UrlImg
            if imagen_file:
                file_bytes = imagen_file.read()
                resultado = r2_storage.upload_logo_empresa(
                    file_bytes=file_bytes,
                    file_name=imagen_file.name
                )

                if resultado['success']:
                    empresa_save.UrlImg = resultado['url']
                    empresa_save.save(update_fields=['UrlImg'])
                else:
                    # Si falló la subida a R2, podés decidir qué hacer:
                    # Opción A: Dejar la empresa sin logo (como ahora)
                    # Opción B: Eliminar la empresa y devolver error
                    print(f"⚠️ Error subiendo logo a R2: {resultado['message']}")

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

            empresa = Empresas.objects.filter(Id=id_empresa)
            if not empresa.exists():
                return Response(
                    {'message': f'No existe una empresa con ID {id_empresa}'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            instancia_empresa = empresa.first()

            nombre_empresa = request.data.get('nombre', '').strip()
            ruc = request.data.get('ruc', '')
            nuevo_logo = request.FILES.get('logo')

            with transaction.atomic():
                # Preparar datos a actualizar (sin logo)
                data_actualizar = {
                    'NombreEmpresa': nombre_empresa,
                    'Ruc': ruc,
                }

                serializer = RegistroEmpresaSerializer(
                    instance=instancia_empresa,
                    data=data_actualizar
                )

                if not serializer.is_valid():
                    mensajes_error = []
                    for campo, mensajes in serializer.errors.items():
                        for mensaje in mensajes:
                            mensajes_error.append(f"{campo}: {mensaje}")

                    error_concatenado = "; ".join(mensajes_error)

                    return Response({
                        'message': error_concatenado,
                        'detalles': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)

                empresa_save = serializer.save()

                # Si hay nuevo logo
                if nuevo_logo:
                    # Eliminar logo anterior de R2 si existe
                    if instancia_empresa.UrlImg:
                        resultado_delete = r2_storage.delete_logo_empresa(
                            instancia_empresa.UrlImg
                        )
                        if not resultado_delete['success']:
                            print(f"⚠️ Error eliminando logo anterior: {resultado_delete}")

                    # Subir nuevo logo a R2
                    file_bytes = nuevo_logo.read()
                    resultado = r2_storage.upload_logo_empresa(
                        file_bytes=file_bytes,
                        file_name=nuevo_logo.name
                    )

                    if resultado['success']:
                        empresa_save.UrlImg = resultado['url']
                        empresa_save.save(update_fields=['UrlImg'])
                    else:
                        print(f"⚠️ Error subiendo nuevo logo a R2: {resultado['message']}")

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
            try:
                id_empresa = int(id_empresa)
            except (TypeError, ValueError):
                return Response(
                    {'message': 'El ID de empresa debe ser un número válido'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            empresa_reg = Empresas.objects.filter(Id=id_empresa)
            if not empresa_reg.exists():
                return Response(
                    {'message': f'No existe una empresa con Id={id_empresa}.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            instancia_empresa = empresa_reg.first()

            # Guardar URL del logo antes de eliminar
            logo_url = instancia_empresa.UrlImg

            with transaction.atomic():
                # Primero eliminar el registro de la base de datos
                instancia_empresa.delete()

                # Luego eliminar el logo de R2 (si existe)
                if logo_url:
                    resultado = r2_storage.delete_logo_empresa(logo_url)
                    if not resultado['success']:
                        print(f"⚠️ Error eliminando logo de R2: {resultado}")

            return Response({
                'message': f'Empresa con ID {id_empresa} eliminada exitosamente'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
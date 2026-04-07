import json
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from django.utils.dateparse import parse_date

from FinTrackApp.Decoradores.DecoradoresSeguridad import AutenticacionToken


from FinTrackApp.Modelos.MovimientosIngresos import MovimientosIngresos
from FinTrackApp.Modelos.MovimientosIngresosDetalles import MovimientosIngresosDetalles

from FinTrackApp.Serializadores.SerializadoresValidaciones.MovimientosIngresosValSerializers import VerificacionIngresoUsuarioSerializer
from FinTrackApp.Serializadores.SerilizadoresModelos.MovimientosIngresosSerializers import InfoMovimientoIngresoSerializer

from FinTrackApp.Utils.supabase_client import *

class RegistroMovimientoIngresoUser(APIView):

    @AutenticacionToken
    def post(self, request, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')

            observacion = request.data.get('observacion', '').strip()
            fecha_str = request.data.get('fecha', '')
            fecha_ingreso = parse_date(fecha_str)

            if fecha_ingreso is None:
                # Manejar error: formato incorrecto
                return Response({'message': 'Formato de fecha inválido. Use YYYY-MM-DD'}, status=400)
            
            ingresos_json_str = request.data.get('ingresos')
            if not ingresos_json_str:
                return Response({'message': 'Falta la key ingresos'}, status=status.HTTP_400_BAD_REQUEST)
            
            data_ingresos = json.loads(ingresos_json_str)
            if not data_ingresos:
                return Response({'message': 'Debe enviar los ingresos a registrar'}, status=status.HTTP_400_BAD_REQUEST)
                
            serializer = VerificacionIngresoUsuarioSerializer(data=data_ingresos, many=True, context={'usuario_id': id_usuario})
            if not serializer.is_valid():
                errores_por_item = serializer.errors  # Lista de dicts, uno por gasto
                mensajes = []
                
                for idx, errores_item in enumerate(errores_por_item):
                    if errores_item:  # Si este gasto tiene errores
                        for campo, lista in errores_item.items():
                            for mensaje in lista:
                                # Puedes incluir el índice (opcional)
                                mensajes.append(f"Ingreso #{idx+1} - {campo}: {mensaje}")
                
                error_concatenado = "; ".join(mensajes)
                return Response({'message': error_concatenado}, status=status.HTTP_400_BAD_REQUEST)
            
            
            
            imagen_url = None
            imagen_file = request.FILES.get('imagen')
            obs_img=""
            if imagen_file:
                # Leer archivo
                file_bytes = imagen_file.read()
                
                # ✅ LLAMADA CORRECTA al método que SÍ existe
                resultado = supabase_storage.upload_ingreso_image(
                    file_bytes=file_bytes,
                    file_name=imagen_file.name  # ← nombre correcto del parámetro
                )
                
                
                if not resultado['success']:
                    obs_img=f'Error al subir imagen: {resultado.get("message")}'
                    
                else:
                    imagen_url = resultado['url']
            
            
            try:
                
                with transaction.atomic():
                    mov_ingreso = MovimientosIngresos.objects.create(
                        Observacion=observacion,
                        Usuario_id=id_usuario,
                        UrlImg=imagen_url,
                        ObsImg=obs_img,
                        FechaIngreso=fecha_str,
                        FechaRegistro=timezone.now()
                        
                        
                    )
                    MovimientosIngresosDetalles.objects.bulk_create([
                            MovimientosIngresosDetalles(
                                MovimientoIngreso_id= mov_ingreso.Id,
                                IngresoUsuario_id=ingreso['idingreso'],
                                MontoIngreso=ingreso['monto']
                            )
                            for ingreso in data_ingresos
                        ])
                    
                    movimiento_registrado = MovimientosIngresos.objects.filter(Id=mov_ingreso.Id).annotate(
                        TotalMovimiento=Sum('movimiento_ingreso_cabecera_detalle__MontoIngreso')).first()
                    
                    detail_serializer = InfoMovimientoIngresoSerializer(movimiento_registrado)
                    return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                # opcionalmente loguear el error
                error_archivo=""
                if imagen_url:
                    resultado = supabase_storage.delete_ingreso_image(imagen_url)
                    if not resultado['success']:
                       error_archivo=f'; el archivo asociado no fue eliminado, el error :{ resultado.get('details', resultado.get('error'))}'
                    else:
                        error_archivo="; el archivo asocioado fue eliminado"
                msg=f'Error al registrar el movimiento: {str(e)} {error_archivo}'
                return Response({'message': msg}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class EditarMovimientoIngresoUser(APIView):
    @AutenticacionToken
    def put(self, request, idmovimiento, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')

            movimiento_obj=MovimientosIngresos.objects.filter(Id=idmovimiento,Usuario_id=id_usuario)
            if not movimiento_obj.exists():
                return Response(
                    {'message': f'No existe un movimiento ingreso con Id={idmovimiento} para este usuario.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            instancia_movimiento=movimiento_obj.first()
            fecha_str = request.data.get('fecha', '')
            fecha_ingreso = parse_date(fecha_str)
            
            if fecha_ingreso is None:
                # Manejar error: formato incorrecto
                return Response({'message': 'Formato de fecha inválido. Use YYYY-MM-DD'}, status=400)
            ################### PARA ACTUALIZACION DE INGRESOS #####################################
            ingresos_json_str = request.data.get('ingresos')
            if not ingresos_json_str:
                return Response({'message': 'Falta la key ingresos'}, status=status.HTTP_400_BAD_REQUEST)
            data_ingresos = json.loads(ingresos_json_str)

            serializer_data_ingresos = VerificacionIngresoUsuarioSerializer(data=data_ingresos, many=True, context={'usuario_id': id_usuario})
            if not serializer_data_ingresos.is_valid():
                errores_por_item = serializer_data_ingresos.errors  # Lista de dicts, uno por gasto
                mensajes = []
                
                for idx, errores_item in enumerate(errores_por_item):
                    if errores_item:  # Si este gasto tiene errores
                        for campo, lista in errores_item.items():
                            for mensaje in lista:
                                # Puedes incluir el índice (opcional)
                                mensajes.append(f"Gasto #{idx+1} - {campo}: {mensaje}")
                
                error_concatenado = "; ".join(mensajes)
                return Response({'message': error_concatenado}, status=status.HTTP_400_BAD_REQUEST)
            
            ingresos_validados = serializer_data_ingresos.validated_data

            movimiento_detalle_obj=MovimientosIngresosDetalles.objects.filter(MovimientoIngreso_id=idmovimiento)
            detalles_dict = {detalle.IngresoUsuario_id: detalle for detalle in movimiento_detalle_obj}
            detalles_a_actualizar = []
            detalles_a_crear = []
            ids_a_eliminar = []
            
            # Recorrer los gastos recibidos
            for ingreso in ingresos_validados:
                idingreso = ingreso['idingreso']
                monto = ingreso['monto']
                if idingreso in detalles_dict:
                    # Actualizar monto del detalle existente
                    detalle = detalles_dict[idingreso]
                    detalle.MontoIngreso = monto
                    detalles_a_actualizar.append(detalle)
                    # Eliminar del diccionario para saber cuáles sobran después
                    del detalles_dict[idingreso]
                else:
                    # Crear nuevo detalle
                    detalles_a_crear.append(
                        MovimientosIngresosDetalles(
                            MovimientoIngreso_id=idmovimiento,
                            IngresoUsuario_id=idingreso,
                            MontoIngreso=monto
                        )
                    )

            # Los detalles que quedan en detalles_dict no están en la data → deben eliminarse
            ids_a_eliminar = list(detalles_dict.keys())
            
            with transaction.atomic():
                imagen_url=instancia_movimiento.UrlImg
                imagen_file = request.FILES.get('imagen')
                imagen_url_new=None
                obs_img=""
                fecha_actual=instancia_movimiento.FechaIngreso
                if imagen_file:
                    if imagen_url:
                        resultado = supabase_storage.delete_ingreso_image(imagen_url)
                        if not resultado['success']:
                            return Response({
                                'message': 'Fallo al eliminar imagen asociada',
                                'detalles': resultado.get('details', resultado.get('error')),
                                'Movimiento': idmovimiento
                            }, status=status.HTTP_400_BAD_REQUEST)
                    # Leer archivo
                    file_bytes = imagen_file.read()
                    
                    
                    resultado = supabase_storage.upload_ingreso_image(
                        file_bytes=file_bytes,
                        file_name=imagen_file.name  # ← nombre correcto del parámetro
                    )
                    obs_img="Actualizada "
                    
                    if not resultado['success']:
                        obs_img=f'Error al subir imagen: {resultado.get("message")}'
                        
                    else:
                        imagen_url_new = resultado['url']
                    
                    movimiento_obj.update(UrlImg=imagen_url_new,ObsImg=obs_img,FechaRegistro=timezone.now())

                
                if fecha_actual != fecha_ingreso:
                    movimiento_obj.update(FechaIngreso=fecha_str,FechaRegistro=timezone.now())
                

                ##################### DETALLE GASTOS ########################
                # 1. Eliminar los detalles sobrantes
                if ids_a_eliminar:
                    MovimientosIngresosDetalles.objects.filter(
                        MovimientoIngreso_id=idmovimiento,
                        IngresoUsuario_id__in=ids_a_eliminar
                    ).delete()

                # 2. Actualizar los detalles existentes (bulk_update)
                if detalles_a_actualizar:
                 
                    MovimientosIngresosDetalles.objects.bulk_update(
                        detalles_a_actualizar, ['MontoIngreso']
                    )
                    
                # 3. Crear los nuevos detalles (bulk_create)
                if detalles_a_crear:
                    MovimientosIngresosDetalles.objects.bulk_create(detalles_a_crear)

                movimiento_obj_act= MovimientosIngresos.objects.filter(Id=idmovimiento).annotate(
                        TotalMovimiento=Sum('movimiento_ingreso_cabecera_detalle__MontoIngreso')).first()
                    
                detail_serializer = InfoMovimientoIngresoSerializer(movimiento_obj_act)
                return Response(
                    {'message': f'El movimiento con id {idmovimiento} ha sido actualizado',
                     'data':detail_serializer.data
                     },
                    status=status.HTTP_200_OK
                )


        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class EliminarMovimientoIngresoUser(APIView):
    @AutenticacionToken
    def delete(self, request, idmovimiento, *args, **kwargs):
        try:

            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')
            movimiento_obj=MovimientosIngresos.objects.filter(Id=idmovimiento,Usuario_id=id_usuario)
            if not movimiento_obj.exists():
                return Response(
                    {'message': f'No existe un movimiento ingreso con Id={idmovimiento} para este usuario.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            instancia_movimiento=movimiento_obj.first()
            try:
                with transaction.atomic():
                    imagen_url=instancia_movimiento.UrlImg # te toma la imagen a eliminar 
                    instancia_movimiento.movimiento_ingreso_cabecera_detalle.all().delete() # se elimina el detalle
                    instancia_movimiento.delete() # se eliminar la cabecera
                    if imagen_url:
                        resultado = supabase_storage.delete_ingreso_image(imagen_url) # se elimina la imagen
                    
            except Exception as e:
                msg=f'Error al eliminar el movimiento de iongreso: {str(e)}'
                return Response({'message': msg}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'message':f'El movimiento con id {idmovimiento} ha sido eliminada'}, status=status.HTTP_200_OK)

        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
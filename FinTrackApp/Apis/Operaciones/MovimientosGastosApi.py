import json
from django.db.models import Sum

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from django.utils.dateparse import parse_date
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from FinTrackApp.Decoradores.DecoradoresSeguridad import AutenticacionToken


from FinTrackApp.Modelos.MovimientosGastos import MovimientosGastos
from FinTrackApp.Modelos.MovimientosGastosDetalles import MovimientosGastosDetalles
from FinTrackApp.Modelos.MovimientosGastosMediosPagos import MovimientosGastosMediosPagos
from FinTrackApp.Modelos.Empresas import Empresas


from FinTrackApp.Modelos.MediosPagos import MediosPagos
from FinTrackApp.Modelos.Gastos import Gastos


from FinTrackApp.Serializadores.SerilizadoresModelos.EmpresasSerializers import InfoEmpresasReferecianlSerializer
from FinTrackApp.Serializadores.SerilizadoresModelos.GastosSerializers import InfoGastoReferencialSerializer
from FinTrackApp.Serializadores.SerilizadoresModelos.MediosPagosSerializers import InfoMedioPagoReferencialSerializer


from FinTrackApp.Serializadores.SerializadoresValidaciones.MovimientosGastosValSerializers import VerificacionGastoUsuarioSerializer,VerificacionMedioPagoUsuarioSerializer
from FinTrackApp.Serializadores.SerilizadoresModelos.MovimientosGastosSerializers import InfoMovimientosGastosSerializer,InfoMovimientosGastosReferencialSerializer

from FinTrackApp.Utils.supabase_client import *


class RegistroMovimientoGastoUser(APIView):

    @AutenticacionToken
    def post(self, request, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')

            observacion = request.data.get('observacion', '').strip()
            fecha_str = request.data.get('fecha', '')
            fecha_gasto = parse_date(fecha_str)
            empresa_id = int(request.data.get('empresa', 1))
            if not Empresas.objects.filter(Id=empresa_id).exists():
                return Response({'message': 'Seleccione una empresa valida'}, status=400)

            if fecha_gasto is None:
                # Manejar error: formato incorrecto
                return Response({'message': 'Formato de fecha inválido. Use YYYY-MM-DD'}, status=400)
            
            gastos_json_str = request.data.get('gastos')
            if not gastos_json_str:
                return Response({'message': 'Falta la key gastos'}, status=status.HTTP_400_BAD_REQUEST)
            
            data_gastos = json.loads(gastos_json_str)
            if not data_gastos:
                return Response({'message': 'Debe enviar los gastos a registrar'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = VerificacionGastoUsuarioSerializer(data=data_gastos, many=True, context={'usuario_id': id_usuario})
            if not serializer.is_valid():
                errores_por_item = serializer.errors  # Lista de dicts, uno por gasto
                mensajes = []
                
                for idx, errores_item in enumerate(errores_por_item):
                    if errores_item:  # Si este gasto tiene errores
                        for campo, lista in errores_item.items():
                            for mensaje in lista:
                                # Puedes incluir el índice (opcional)
                                mensajes.append(f"Gasto #{idx+1} - {campo}: {mensaje}")
                
                error_concatenado = "; ".join(mensajes)
                return Response({'message': error_concatenado}, status=status.HTTP_400_BAD_REQUEST)
                        
            medios_json_str = request.data.get('medios')
            if not medios_json_str:
                return Response({'message': 'Falta la key medios'}, status=status.HTTP_400_BAD_REQUEST)

            data_medios = json.loads(medios_json_str)
            if not data_medios:
                return Response({'message': 'Debe enviar los medios de pagos a registrar'}, status=status.HTTP_400_BAD_REQUEST) 
            
            
            serializer = VerificacionMedioPagoUsuarioSerializer(data=data_medios, many=True, context={'usuario_id': id_usuario})
            if not serializer.is_valid():
                errores_por_item = serializer.errors  # Lista de dicts, uno por gasto
                mensajes = []
                
                for idx, errores_item in enumerate(errores_por_item):
                    if errores_item:  # Si este gasto tiene errores
                        for campo, lista in errores_item.items():
                            for mensaje in lista:
                                # Puedes incluir el índice (opcional)
                                mensajes.append(f"Medio #{idx+1} - {campo}: {mensaje}")
                
                error_concatenado = "; ".join(mensajes)
                return Response({'message': error_concatenado}, status=status.HTTP_400_BAD_REQUEST)
            
            total_gasto = sum(gasto['monto'] for gasto in data_gastos)
            total_medio = sum(medio['monto'] for medio in data_medios)

            if total_gasto != total_medio:
                return Response({'message': 'La distribucion entre medios de pagos y detalle de gastos no coinciden!'}, status=status.HTTP_400_BAD_REQUEST) 
            
            imagen_url = None
            imagen_file = request.FILES.get('imagen')
            obs_img=""
            if imagen_file:
                
                # Leer archivo
                file_bytes = imagen_file.read()
                
                # ✅ LLAMADA CORRECTA al método que SÍ existe
                resultado = supabase_storage.upload_gasto_image(
                    file_bytes=file_bytes,
                    file_name=imagen_file.name  # ← nombre correcto del parámetro
                )
                obs_img=""
                
                if not resultado['success']:
                    obs_img=f'Error al subir imagen: {resultado.get("message")}'
                    
                else:
                    imagen_url = resultado['url']
            
            
            
            try:
                
                with transaction.atomic():
                    mov_gasto = MovimientosGastos.objects.create(
                        Observacion=observacion,
                        Usuario_id=id_usuario,
                        UrlImg=imagen_url,
                        ObsImg=obs_img,
                        FechaGasto=fecha_str,
                        FechaRegistro=timezone.now(),
                        Empresa_id=empresa_id
                        
                        
                    )
                    MovimientosGastosDetalles.objects.bulk_create([
                            MovimientosGastosDetalles(
                                MovimientoGasto_id= mov_gasto.Id,
                                GastoUsuario_id=gasto['idgasto'],
                                MontoGasto=gasto['monto']
                            )
                            for gasto in data_gastos
                        ])
                    
                    MovimientosGastosMediosPagos.objects.bulk_create([
                            MovimientosGastosMediosPagos(
                                MovimientoGasto_id= mov_gasto.Id,
                                MedioPago_id=medio['idmedio'],
                                MontoMedioPago=medio['monto']
                            )
                            for medio in data_medios
                        ])
                    
                    movimiento_registrado = MovimientosGastos.objects.filter(Id=mov_gasto.Id).annotate(
                        TotalMovimiento=Sum('movimiento_gasto_cabecera_detalle__MontoGasto')).first()

                    detail_serializer = InfoMovimientosGastosSerializer(movimiento_registrado)

                    return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                # opcionalmente loguear el error
                error_archivo=""
                if imagen_url:
                    resultado = supabase_storage.delete_gasto_image(imagen_url)
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
        
class EditarMovimientoGastoUser(APIView):
    @AutenticacionToken
    def put(self, request, idmovimiento, *args, **kwargs):
        try:

            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')

            movimiento_obj=MovimientosGastos.objects.filter(Id=idmovimiento,Usuario_id=id_usuario)
            if not movimiento_obj.exists():
                return Response(
                    {'message': f'No existe un movimiento gasto con Id={idmovimiento} para este usuario.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            instancia_movimiento=movimiento_obj.first()
            fecha_str = request.data.get('fecha', '')
            fecha_gasto = parse_date(fecha_str)
            
            if fecha_gasto is None:
                # Manejar error: formato incorrecto
                return Response({'message': 'Formato de fecha inválido. Use YYYY-MM-DD'}, status=400)
            ################### PARA ACTUALIZACION DE GASTOS #####################################
            gastos_json_str = request.data.get('gastos')
            if not gastos_json_str:
                return Response({'message': 'Falta la key gastos'}, status=status.HTTP_400_BAD_REQUEST)
            data_gastos = json.loads(gastos_json_str)

            serializer_data_gastos = VerificacionGastoUsuarioSerializer(data=data_gastos, many=True, context={'usuario_id': id_usuario})
            if not serializer_data_gastos.is_valid():
                errores_por_item = serializer_data_gastos.errors  # Lista de dicts, uno por gasto
                mensajes = []
                
                for idx, errores_item in enumerate(errores_por_item):
                    if errores_item:  # Si este gasto tiene errores
                        for campo, lista in errores_item.items():
                            for mensaje in lista:
                                # Puedes incluir el índice (opcional)
                                mensajes.append(f"Gasto #{idx+1} - {campo}: {mensaje}")
                
                error_concatenado = "; ".join(mensajes)
                return Response({'message': error_concatenado}, status=status.HTTP_400_BAD_REQUEST)
            gastos_validados = serializer_data_gastos.validated_data

            movimiento_detalle_obj=MovimientosGastosDetalles.objects.filter(MovimientoGasto_id=idmovimiento)
            detalles_dict = {detalle.GastoUsuario_id: detalle for detalle in movimiento_detalle_obj}
            detalles_a_actualizar = []
            detalles_a_crear = []
            ids_a_eliminar = []

            # Recorrer los gastos recibidos
            for gasto in gastos_validados:
                idgasto = gasto['idgasto']
                monto = gasto['monto']
                if idgasto in detalles_dict:
                    # Actualizar monto del detalle existente
                    detalle = detalles_dict[idgasto]
                    detalle.MontoGasto = monto
                    detalles_a_actualizar.append(detalle)
                    # Eliminar del diccionario para saber cuáles sobran después
                    del detalles_dict[idgasto]
                else:
                    # Crear nuevo detalle
                    detalles_a_crear.append(
                        MovimientosGastosDetalles(
                            MovimientoGasto_id=idmovimiento,
                            GastoUsuario_id=idgasto,
                            MontoGasto=monto
                        )
                    )

            # Los detalles que quedan en detalles_dict no están en la data → deben eliminarse
            ids_a_eliminar = list(detalles_dict.keys())

            ################### PARA ACTUALIZACION DE MEDIOS #####################################
            medios_json_str = request.data.get('medios')
            if not medios_json_str:
                return Response({'message': 'Falta la key medios'}, status=status.HTTP_400_BAD_REQUEST)
            data_medios = json.loads(medios_json_str)
            
            serializer_data_medios = VerificacionMedioPagoUsuarioSerializer(data=data_medios, many=True, context={'usuario_id': id_usuario})
            if not serializer_data_medios.is_valid():
                errores_por_item = serializer_data_medios.errors  # Lista de dicts, uno por gasto
                mensajes = []
                
                for idx, errores_item in enumerate(errores_por_item):
                    if errores_item:  # Si este gasto tiene errores
                        for campo, lista in errores_item.items():
                            for mensaje in lista:
                                # Puedes incluir el índice (opcional)
                                mensajes.append(f"Medio #{idx+1} - {campo}: {mensaje}")
                
                error_concatenado = "; ".join(mensajes)
                return Response({'message': error_concatenado}, status=status.HTTP_400_BAD_REQUEST)
            
            medios_validados = serializer_data_medios.validated_data

            movimiento_medios_obj=MovimientosGastosMediosPagos.objects.filter(MovimientoGasto_id=idmovimiento)
            detalles_medios_dict = {detalle.MedioPago_id: detalle for detalle in movimiento_medios_obj}
            detalles_medios_a_actualizar = []
            detalles_medios_a_crear = []
            ids_medios_a_eliminar = []

            # Recorrer los gastos recibidos
            for medio in medios_validados:
                idmedio = medio['idmedio']
                monto = medio['monto']
                if idmedio in detalles_medios_dict:
                    # Actualizar monto del detalle existente
                    detalle = detalles_medios_dict[idmedio]
                    detalle.MontoMedioPago = monto
                    detalles_medios_a_actualizar.append(detalle)
                    # Eliminar del diccionario para saber cuáles sobran después
                    del detalles_medios_dict[idmedio]
                else:
                    # Crear nuevo detalle
                    detalles_medios_a_crear.append(
                        MovimientosGastosMediosPagos(
                            MovimientoGasto_id=idmovimiento,
                            MedioPago_id=idmedio,
                            MontoMedioPago=monto
                        )
                    )

            # Los detalles que quedan en detalles_dict no están en la data → deben eliminarse
            ids_medios_a_eliminar = list(detalles_medios_dict.keys())
           
            ######################################### CONTROL GASTOS VS MEDIOS PAGOS #############################################
            total_gasto = sum(gasto['monto'] for gasto in data_gastos)
            total_medio = sum(medio['monto'] for medio in data_medios)

            if total_gasto != total_medio:
                return Response({'message': 'La distribucion entre medios de pagos y detalle de gastos no coinciden!'}, status=status.HTTP_400_BAD_REQUEST)

            
            with transaction.atomic():
                imagen_url=instancia_movimiento.UrlImg
                imagen_file = request.FILES.get('imagen')
                imagen_url_new=None
                obs_img=""
                fecha_actual=instancia_movimiento.FechaGasto
                if imagen_file:
                    if imagen_url:
                        resultado = supabase_storage.delete_gasto_image(imagen_url)
                        if not resultado['success']:
                            return Response({
                                'message': 'Fallo al eliminar imagen asociada',
                                'detalles': resultado.get('details', resultado.get('error')),
                                'Movimiento': idmovimiento
                            }, status=status.HTTP_400_BAD_REQUEST)
                    # Leer archivo
                    file_bytes = imagen_file.read()
                    
                    
                    resultado = supabase_storage.upload_gasto_image(
                        file_bytes=file_bytes,
                        file_name=imagen_file.name  # ← nombre correcto del parámetro
                    )
                    obs_img="Actualizada "
                    
                    if not resultado['success']:
                        obs_img=f'Error al subir imagen: {resultado.get("message")}'
                        
                    else:
                        imagen_url_new = resultado['url']
                    
                    movimiento_obj.update(UrlImg=imagen_url_new,ObsImg=obs_img,FechaRegistro=timezone.now())

                if fecha_actual != fecha_gasto:
                    movimiento_obj.update(FechaGasto=fecha_str,FechaRegistro=timezone.now())
                        



                ##################### DETALLE GASTOS ########################
                # 1. Eliminar los detalles sobrantes
                if ids_a_eliminar:
                    MovimientosGastosDetalles.objects.filter(
                        MovimientoGasto_id=idmovimiento,
                        GastoUsuario_id__in=ids_a_eliminar
                    ).delete()

                # 2. Actualizar los detalles existentes (bulk_update)
                if detalles_a_actualizar:
                    MovimientosGastosDetalles.objects.bulk_update(
                        detalles_a_actualizar, ['MontoGasto']
                    )

                # 3. Crear los nuevos detalles (bulk_create)
                if detalles_a_crear:
                    MovimientosGastosDetalles.objects.bulk_create(detalles_a_crear)

                ##################### MEDIOS PAGOS ########################
                # 1. Eliminar los detalles sobrantes
                if ids_medios_a_eliminar:
                    MovimientosGastosMediosPagos.objects.filter(
                        MovimientoGasto_id=idmovimiento,
                        MedioPago_id__in=ids_medios_a_eliminar
                    ).delete()

                # 2. Actualizar los detalles existentes (bulk_update)
                if detalles_medios_a_actualizar:
                    MovimientosGastosMediosPagos.objects.bulk_update(
                        detalles_medios_a_actualizar, ['MontoMedioPago']
                    )

                # 3. Crear los nuevos detalles (bulk_create)
                if detalles_medios_a_crear:
                    MovimientosGastosMediosPagos.objects.bulk_create(detalles_medios_a_crear)

                movimiento_obj_act=MovimientosGastos.objects.filter(Id=idmovimiento).annotate(
                        TotalMovimiento=Sum('movimiento_gasto_cabecera_detalle__MontoGasto')
                    ).first()

                detail_serializer = InfoMovimientosGastosSerializer(movimiento_obj_act)
                return Response(
                    {'message': f'El movimiento con id {idmovimiento} ha sido actualizado',
                     'data':detail_serializer.data
                     },
                    status=status.HTTP_200_OK
                )

        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EliminarMovimientoGastoUser(APIView):
    @AutenticacionToken
    def delete(self, request, idmovimiento, *args, **kwargs):
        try:

            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')
            movimiento_obj=MovimientosGastos.objects.filter(Id=idmovimiento,Usuario_id=id_usuario)
            if not movimiento_obj.exists():
                return Response(
                    {'message': f'No existe un movimiento gasto con Id={idmovimiento} para este usuario.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            instancia_movimiento=movimiento_obj.first()
            try:
                with transaction.atomic():
                    imagen_url=instancia_movimiento.UrlImg # te toma la imagen a eliminar 
                    instancia_movimiento.movimiento_gasto_cabecera_detalle.all().delete() # se elimina el detalle
                    instancia_movimiento.movimiento_gasto_cabecera_medio.all().delete() # se eliminar los medios de pagos
                    instancia_movimiento.delete() # se eliminar la cabecera
                    if imagen_url:
                        resultado = supabase_storage.delete_gasto_image(imagen_url) # se elimina la imagen
                    
            except Exception as e:
                msg=f'Error al eliminar el movimiento de gasto: {str(e)}'
                return Response({'message': msg}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'message':f'El movimiento con id {idmovimiento} ha sido eliminada'}, status=status.HTTP_200_OK)

        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
# class ReferencialesCargaGasto(APIView):
#     @AutenticacionToken
#     def get(self, request, *args, **kwargs):
#         try:

#             user_info = getattr(request, 'user_info', {})
#             user_login = user_info["username"]
#             id_usuario=user_info.get('usuario_id')
            
#             medios_pago_obj=MediosPagos.objects.filter(Usuario_id=id_usuario)
#             medio_serializer = InfoMedioPagoReferencialSerializer(medios_pago_obj,many=True)

#             gastos_usuario=Gastos.objects.filter(Usuario_id=id_usuario)
#             gasto_serializer = InfoGastoReferencialSerializer(gastos_usuario,many=True)

#             empresas = Empresas.objects.all()
#             empresa_serializer = InfoEmpresasReferecianlSerializer(empresas, many=True)

#             fecha_limite = now() - relativedelta(months=6)

#             movimientos_gastos_usuario = MovimientosGastos.objects.filter(
#                 Usuario_id=id_usuario,
#                 FechaGasto__gte=fecha_limite
#             )
#             movimientos_serializer = InfoMovimientosGastosReferencialSerializer(movimientos_gastos_usuario,many=True)
#             resumen = resumen_movimientos_gastos_usuario(movimientos_serializer.data)
#             data={
#                 'Movimientos':resumen,
#                 'MediosPagos':medio_serializer.data,
#                 'Gastos':gasto_serializer.data,
#                 'Empresa':empresa_serializer.data
#             }


#             return Response(data, status=status.HTTP_200_OK)

#         except Exception as e:
            
#             return Response(
#                  {'message': f'Error interno del servidor: {str(e)}'}, 
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
class ReferencialesCargaGasto(APIView):
    @AutenticacionToken
    def get(self, request, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario = user_info.get('usuario_id')
            
            # Obtener datos
            fecha_limite = now() - relativedelta(months=6)
            movimientos_gastos_usuario = MovimientosGastos.objects.filter(
                Usuario_id=id_usuario,
                FechaGasto__gte=fecha_limite
            )
            movimientos_serializer = InfoMovimientosGastosReferencialSerializer(movimientos_gastos_usuario, many=True)
            
            
            # Obtener resumen de cantidades
            resumen = resumen_movimientos_gastos_usuario(movimientos_serializer.data)
            
            # Obtener datos de referenciales
            medios_pago_obj = MediosPagos.objects.filter(Usuario_id=id_usuario)
            medio_serializer = InfoMedioPagoReferencialSerializer(medios_pago_obj, many=True)
            
            gastos_usuario = Gastos.objects.filter(Usuario_id=id_usuario)
            gasto_serializer = InfoGastoReferencialSerializer(gastos_usuario, many=True)
            
            empresas = Empresas.objects.all()
            empresa_serializer = InfoEmpresasReferecianlSerializer(empresas, many=True)
            
            # Ordenar según frecuencia de uso
            medios_ordenados = ordenar_por_frecuencia(
                medio_serializer.data, 
                resumen['CantidadMedios'],
                'NombreMedioPago'  # Ajusta este key según tu serializer
            )
            
            gastos_ordenados = ordenar_por_frecuencia(
                gasto_serializer.data,
                resumen['CantidadGastos'],
                'NombreGasto'  # Ajusta este key según tu serializer
            )
            
            empresas_ordenadas = ordenar_por_frecuencia(
                empresa_serializer.data,
                resumen['CantidadEmpresa'],
                'NombreEmpresa'  # Ajusta este key según tu serializer
            )
            
            data = {
                'Movimientos': resumen,
                'MediosPagos': medios_ordenados,
                'Gastos': gastos_ordenados,
                'Empresa': empresas_ordenadas
            }
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

from collections import Counter
def resumen_movimientos_gastos_usuario(movimientos_data):
    """
    Genera resumen de cantidades por ID
    """
    return {
        'CantidadEmpresa': dict(Counter(m['Empresa'] for m in movimientos_data)),
        'CantidadGastos': dict(Counter(
            gasto['GastoUsuario'] 
            for movimiento in movimientos_data 
            for gasto in movimiento.get('DetalleGastos', [])
        )),
        'CantidadMedios': dict(Counter(
            medio['MedioPago'] 
            for movimiento in movimientos_data 
            for medio in movimiento.get('DetalleMediosPagos', [])
        ))
    }

def ordenar_por_frecuencia(items_data, cantidades_dict, nombre_key='Nombre'):
    """
    Ordena los items: los que tienen uso primero (mayor frecuencia), 
    luego los no usados ordenados alfabéticamente por nombre
    """
    # Convertir todas las claves del diccionario a string para comparación consistente
    cantidades_dict_str = {str(k): v for k, v in cantidades_dict.items()}
    
    # Separar y ordenar
    items_con_frecuencia = []
    items_sin_uso = []
    
    for item in items_data:
        item_id_str = str(item['Id'])
        if item_id_str in cantidades_dict_str:
            items_con_frecuencia.append({
                'item': item,
                'frecuencia': cantidades_dict_str[item_id_str]
            })
        else:
            items_sin_uso.append(item)
    
    # Ordenar usados por frecuencia (mayor a menor)
    items_con_frecuencia.sort(key=lambda x: x['frecuencia'], reverse=True)
   
    # Ordenar no usados alfabéticamente
    items_sin_uso.sort(key=lambda x: x[nombre_key].lower())
    
    # Extraer solo los items de los usados
    items_usados_ordenados = [x['item'] for x in items_con_frecuencia]
    
    return items_usados_ordenados + items_sin_uso



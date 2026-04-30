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


from FinTrackApp.Modelos.MovimientosIngresos import MovimientosIngresos
from FinTrackApp.Modelos.Ingresos import Ingresos
from FinTrackApp.Modelos.Empresas import Empresas


from FinTrackApp.Serializadores.SerializadoresValidaciones.MovimientosIngresosValSerializers import VerificacionIngresoUsuarioSerializer
from FinTrackApp.Serializadores.SerilizadoresModelos.MovimientosIngresosSerializers import InfoMovimientoIngresoSerializer
from FinTrackApp.Serializadores.SerilizadoresModelos.IngresosSerializers import InfoIngresoSerializer
from FinTrackApp.Serializadores.SerilizadoresModelos.EmpresasSerializers import InfoEmpresasReferecianlSerializer
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
            empresa=int(request.data.get('empresa'))
            id_ingreso=int(request.data.get('codingreso'))
            monto_ingreso=int(request.data.get('montoingreso'))
            if fecha_ingreso is None:
                # Manejar error: formato incorrecto
                return Response({'message': 'Formato de fecha inválido. Use YYYY-MM-DD'}, status=400)
            
            if not Ingresos.objects.filter(Id=id_ingreso,Usuario_id=id_usuario).exists():
                return Response({'message': 'Seleccione un ingreso valido'}, status=400)
            
            if not Empresas.objects.filter(Id=empresa).exists():
                return Response({'message': 'Seleccione una empresa valida'}, status=400)
            
            if monto_ingreso<1:
                return Response({'message': 'Seleccione un monto valido'}, status=400)
            
            
            
            
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
                        IngresoUsuario_id=id_ingreso,
                        MontoIngreso=monto_ingreso,
                        Empresa_id=empresa,
                        UrlImg=imagen_url,
                        ObsImg=obs_img,
                        FechaIngreso=fecha_str,
                        FechaRegistro=timezone.now()
                        
                        
                    )
                    
                    movimiento_registrado = MovimientosIngresos.objects.filter(Id=mov_ingreso.Id).first()
                    
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
            empresa=int(request.data.get('empresa'))
            id_ingreso=int(request.data.get('codingreso'))
            monto_ingreso=int(request.data.get('montoingreso'))
            
            if fecha_ingreso is None:
                # Manejar error: formato incorrecto
                return Response({'message': 'Formato de fecha inválido. Use YYYY-MM-DD'}, status=400)
            ################### PARA ACTUALIZACION DE INGRESOS #####################################
            
            
            if not Ingresos.objects.filter(Id=id_ingreso,Usuario_id=id_usuario).exists():
                return Response({'message': 'Seleccione un ingreso valido'}, status=400)
            
            if not Empresas.objects.filter(Id=empresa).exists():
                return Response({'message': 'Seleccione una empresa valida'}, status=400)
            
            
            
            with transaction.atomic():
                imagen_url=instancia_movimiento.UrlImg
                imagen_file = request.FILES.get('imagen')
                imagen_url_new=None
                obs_img=""
                fecha_actual=instancia_movimiento.FechaIngreso
                cod_ingreso_actual=instancia_movimiento.IngresoUsuario
                monto_actual=instancia_movimiento.MontoIngreso
                empresa_actual=instancia_movimiento.Empresa
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

                if empresa != empresa_actual:
                    movimiento_obj.update(Empresa=empresa,FechaRegistro=timezone.now())

                if  monto_actual != monto_ingreso:
                    movimiento_obj.update(MontoIngreso=monto_ingreso,FechaRegistro=timezone.now())
                
                if  cod_ingreso_actual != id_ingreso:
                    movimiento_obj.update(IngresoUsuario=id_ingreso,FechaRegistro=timezone.now())
                

                #

                
                return Response(
                    {'message': f'El movimiento con id {idmovimiento} ha sido actualizado',},
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
        

class ReferencialesCargaIngreso(APIView):
    @AutenticacionToken
    def get(self, request, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario = user_info.get('usuario_id')
            
            # Obtener datos
            fecha_limite = now() - relativedelta(months=6)
            movimientos_gastos_usuario = MovimientosIngresos.objects.filter(
                Usuario_id=id_usuario,
                FechaIngreso__gte=fecha_limite
            )
            movimientos_serializer = InfoMovimientoIngresoSerializer(movimientos_gastos_usuario, many=True)
            
            
            # Obtener resumen de cantidades
            resumen = resumen_movimientos_ingresos_usuario(movimientos_serializer.data)
            
            # Obtener datos de referenciales
            
            
            ingresos_usuario = Ingresos.objects.filter(Usuario_id=id_usuario)
            ingresos_serializer = InfoIngresoSerializer(ingresos_usuario, many=True)
            
            empresas = Empresas.objects.all()
            empresa_serializer = InfoEmpresasReferecianlSerializer(empresas, many=True)
            
            
            
            ingresos_ordenados = ordenar_por_frecuencia(
                ingresos_serializer.data,
                resumen['CantidadIngresos'],
                'NombreIngreso'  # Ajusta este key según tu serializer
            )
            
            empresas_ordenadas = ordenar_por_frecuencia(
                empresa_serializer.data,
                resumen['CantidadEmpresa'],
                'NombreEmpresa'  # Ajusta este key según tu serializer
            )
            
            data = {
                
                
                'Ingresos': ingresos_ordenados,
                'Empresa': empresas_ordenadas
            }
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

from collections import Counter
def resumen_movimientos_ingresos_usuario(movimientos_data):
    """
    Genera resumen de cantidades por ID
    """
    return {
        'CantidadEmpresa': dict(Counter(m['Empresa'] for m in movimientos_data)),
        'CantidadIngresos': dict(Counter(m['IngresoUsuario'] for m in movimientos_data))
        
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
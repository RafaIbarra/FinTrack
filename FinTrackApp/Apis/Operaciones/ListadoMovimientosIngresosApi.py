from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Sum

from FinTrackApp.Modelos.MovimientosIngresos import MovimientosIngresos
from FinTrackApp.Serializadores.SerilizadoresModelos.MovimientosIngresosSerializers import InfoMovimientoIngresoSerializer

from FinTrackApp.Decoradores.DecoradoresSeguridad import AutenticacionToken


class ListadoMovimientosIngresosUser(APIView):

    @AutenticacionToken
    def get(self, request, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')
            movimientos_ingresos_usuario = MovimientosIngresos.objects.filter(
                Usuario_id=id_usuario
            ).order_by('Id')
            if not movimientos_ingresos_usuario.exists():
                return Response(
                    {'message': f'El usuario no tiene movimiento de ingresos registrados.'},
                    status=status.HTTP_200_OK
                )
            detail_serializer = InfoMovimientoIngresoSerializer(movimientos_ingresos_usuario,many=True)
            return Response(detail_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ListadoMovimientosIngresosMesUser(APIView):

    @AutenticacionToken
    def get(self, request, anno,mes,*args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')
            movimientos_ingresos_usuario = MovimientosIngresos.objects.filter(
                Usuario_id=id_usuario,
                FechaIngreso__year=anno,  # Filtrar por año
                FechaIngreso__month=mes
            ).order_by('Id')


            
                
            data_detalle=[]
            data_resumen=[
                {

                'TotalGastos':0,
                'CantidadGastos':0,
                'TotalIngresos':0,
                'CantidadIngresos':0,
                }
            ]
            if movimientos_ingresos_usuario.exists():
                detail_serializer = InfoMovimientoIngresoSerializer(movimientos_ingresos_usuario,many=True)
                data_list = detail_serializer.data
                total_elementos = len(data_list)
                suma_total_movimientos = sum(item['MontoIngreso'] for item in data_list)
                data_resumen[0]['TotalIngresos'] = suma_total_movimientos
                data_resumen[0]['CantidadIngresos'] = total_elementos
                data_detalle=detail_serializer.data
            data={
                'detalle':data_detalle,
                'resumen':data_resumen
            }
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

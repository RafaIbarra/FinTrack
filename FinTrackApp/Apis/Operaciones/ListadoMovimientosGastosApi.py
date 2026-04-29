from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Sum

from FinTrackApp.Modelos.MovimientosGastos import MovimientosGastos
from FinTrackApp.Modelos.MovimientosIngresos import MovimientosIngresos
from FinTrackApp.Modelos.MovimientosGastosDetalles import MovimientosGastosDetalles
from FinTrackApp.Serializadores.SerilizadoresModelos.MovimientosGastosSerializers import InfoMovimientosGastosSerializer,InfoMovimientosGastosDetallesSerializer,InfoReferencialesCargaMovimientoGastoSerializer

from FinTrackApp.Decoradores.DecoradoresSeguridad import AutenticacionToken
class ListadoMovimientoGastosUser(APIView):

    @AutenticacionToken
    def get(self, request, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')
            movimientos_gastos_usuario = MovimientosGastos.objects.filter(
                Usuario_id=id_usuario
            ).annotate(
                TotalMovimiento=Sum('movimiento_gasto_cabecera_detalle__MontoGasto')
            ).order_by('Id')
            if not movimientos_gastos_usuario.exists():
                return Response(
                    {'message': f'El usuario no tiene movimiento de gastos registrados.'},
                    status=status.HTTP_200_OK
                )
            detail_serializer = InfoMovimientosGastosSerializer(movimientos_gastos_usuario,many=True)
            return Response(detail_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ListadoMovimientoGastosMesUser(APIView):

    @AutenticacionToken
    def get(self, request,anno,mes, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')

            #mes=10
            movimientos_gastos_usuario = MovimientosGastos.objects.filter(
                Usuario_id=id_usuario,
                FechaGasto__year=anno,  # Filtrar por año
                FechaGasto__month=mes 
            ).annotate(
                TotalMovimiento=Sum('movimiento_gasto_cabecera_detalle__MontoGasto')
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
            

            if  movimientos_gastos_usuario.exists():
                
            
                detail_serializer = InfoMovimientosGastosSerializer(movimientos_gastos_usuario,many=True)
                data_list = detail_serializer.data

                # Contar elementos
                total_elementos = len(data_list)

                # Sumar TotalMovimiento
                suma_total_movimientos = sum(item['TotalMovimiento'] for item in data_list)
                data_detalle=detail_serializer.data

                data_resumen[0]['TotalGastos'] = suma_total_movimientos
                data_resumen[0]['CantidadGastos'] = total_elementos

            
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

class ListadoDetalleGastosUser(APIView):

    @AutenticacionToken
    def get(self, request, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')
            
            detalles_gastos_usuario = MovimientosGastosDetalles.objects.filter(
                MovimientoGasto__Usuario_id=id_usuario
            ).order_by('Id')

            if not detalles_gastos_usuario.exists():
                return Response(
                    {'message': f'El usuario no tiene movimiento de gastos registrados.'},
                    status=status.HTTP_200_OK
                )
            total = MovimientosGastosDetalles.objects.filter(
                MovimientoGasto__Usuario_id=id_usuario
            ).aggregate(total=Sum('MontoGasto'))['total']
            
            detail_serializer = InfoMovimientosGastosDetallesSerializer(detalles_gastos_usuario,many=True)
            return Response(detail_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class DatosReferencialesCargosMovimiento(APIView):

    @AutenticacionToken
    def get(self, request,id, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')

            #mes=10
            movimientos_gastos_usuario = MovimientosGastos.objects.filter(Id=id)
            
            data_detalle=[]
            
            
            

            if  movimientos_gastos_usuario.exists():
            
                detail_serializer = InfoReferencialesCargaMovimientoGastoSerializer(movimientos_gastos_usuario,many=True)
                
                return Response(detail_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
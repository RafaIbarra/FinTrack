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
            ).annotate(
                TotalMovimiento=Sum('movimiento_ingreso_cabecera_detalle__MontoIngreso')
            ).order_by('Id')
            if not movimientos_ingresos_usuario.exists():
                return Response(
                    {'message': f'El usuario no tiene movimiento de ingresos registrados.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            detail_serializer = InfoMovimientoIngresoSerializer(movimientos_ingresos_usuario,many=True)
            return Response(detail_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

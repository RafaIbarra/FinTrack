import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from FinTrackApp.Modelos.MovimientosGastosDetalles import MovimientosGastosDetalles
from FinTrackApp.Serializadores.SerilizadoresModelos.MovimientosGastosSerializers import InfoMovimientosGastosSerializer,InfoMovimientosGastosDetallesSerializer

from FinTrackApp.Decoradores.DecoradoresSeguridad import AutenticacionToken
class ConsultaGastosUser(APIView):

    @AutenticacionToken
    def post(self, request, *args, **kwargs):
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
                    status=status.HTTP_404_NOT_FOUND
                )
            detail_serializer = InfoMovimientosGastosDetallesSerializer(detalles_gastos_usuario,many=True)

            pregunta = request.data.get('pregunta')
            if not pregunta:
                return Response(
                    {'message': 'El campo pregunta es requerido.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            # 3. Enviar al Worker
            try:
                worker_response = requests.post(
                    settings.WORKER_URL,
                    json={
                        'pregunta': pregunta,
                        'gastos': detail_serializer.data
                    },
                    headers={
                        'Content-Type': 'application/json',
                        'X-Worker-Secret': settings.WORKER_SECRET
                    },
                    timeout=30
                )
                # worker_response.raise_for_status()

            except requests.exceptions.Timeout:
                return Response(
                    {'message': 'El asistente tardó demasiado en responder. Intentá de nuevo.'},
                    status=status.HTTP_504_GATEWAY_TIMEOUT
                )
            except requests.exceptions.RequestException as e:
                return Response(
                    {'message': f'Error al comunicarse con el asistente.  {str(e)}'},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            # 4. Retornar la respuesta del Worker al frontend
            return Response(worker_response.json(), status=status.HTTP_200_OK)






        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
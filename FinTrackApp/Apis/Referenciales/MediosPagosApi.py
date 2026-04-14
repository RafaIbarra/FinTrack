from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from FinTrackApp.Decoradores.DecoradoresSeguridad import AutenticacionToken
from FinTrackApp.Modelos.MediosPagos import MediosPagos
from FinTrackApp.Serializadores.SerilizadoresModelos.MediosPagosSerializers import RegistroMedioPagoSerializer,InfoMedioPagoSerializer

class ListadoMedioPagosUser(APIView):
    @AutenticacionToken
    def get(self, request, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')
            medios_pago_obj=MediosPagos.objects.filter(Usuario_id=id_usuario)
            if not medios_pago_obj.exists():
                return Response(
                    {'message': f'El usuario no tiene medios de pagos registradss.'},
                    status=status.HTTP_200_OK
                )
            detail_serializer = InfoMedioPagoSerializer(medios_pago_obj,many=True)
            return Response(detail_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OperacionesMediosPagosUser(APIView):

    @AutenticacionToken
    def post(self, request, *args, **kwargs):
        try:
            
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')

            nombre=request.data.get('nombre').strip()
            descripcion = request.data.get('descripcion', '').strip()
        
            data_registrar={
              'NombreMedioPago':nombre,
              'Observacion':descripcion,
              'Usuario':id_usuario,
            }
            serializer = RegistroMedioPagoSerializer(data=data_registrar)
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
            
            categoria = serializer.save()
            detail_serializer = InfoMedioPagoSerializer(categoria)
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @AutenticacionToken
    def put(self, request, idmedio,*args, **kwargs):
        try:
            
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')

            nombre=request.data.get('nombre').strip()
            descripcion = request.data.get('descripcion', '').strip()
            medio_pago_obj=MediosPagos.objects.filter(Id=idmedio,Usuario_id=id_usuario)
            if not medio_pago_obj.exists():
                return Response(
                    {'message': f'No existe un medio de pago con Id={idmedio} para este usuario.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            instancia_medio=medio_pago_obj.first()
            data_registrar={
              'Id':idmedio,
              'NombreMedioPago':nombre,
              'Observacion':descripcion,
              'Usuario':id_usuario,
            }
            serializer = RegistroMedioPagoSerializer(instance=instancia_medio,data=data_registrar)
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
            
            medio_pago = serializer.save()
            detail_serializer = InfoMedioPagoSerializer(medio_pago)
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
   
   
    @AutenticacionToken
    def delete(self, request, idmedio, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')
            medio_pago_obj=MediosPagos.objects.filter(Id=idmedio,Usuario_id=id_usuario)
            if not medio_pago_obj.exists():
                return Response(
                    {'message': f'No existe un  medio de pago con Id={idmedio} para este usuario.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            instancia_medio=medio_pago_obj.first()
            instancia_medio.delete()
            return Response({'message':f'El medio con id {idmedio} ha sido eliminada'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
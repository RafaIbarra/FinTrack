from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from FinTrackApp.Decoradores.DecoradoresSeguridad import AutenticacionToken

from FinTrackApp.Modelos.Gastos import Gastos
from FinTrackApp.Modelos.CategoriasGastos import CategoriasGastos
from FinTrackApp.Modelos.TiposGastos import TiposGastos

from FinTrackApp.Serializadores.SerilizadoresModelos.GastosSerializers import RegistroGastoSerializer,InfoGastoSerializer
class OperacionesGastosUsuario(APIView):

    @AutenticacionToken
    def post(self, request, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')

            nombre=request.data.get('nombre').strip()
            observacion = request.data.get('observacion', '').strip()
            id_categoria=int(request.data.get('categoria'))
            id_tipo_gasto=int(request.data.get('tipo_gasto'))
            categoria_obj=CategoriasGastos.objects.filter(Id=id_categoria,Usuario_id=id_usuario)
            tipogasto_obj=TiposGastos.objects.filter(Id=id_tipo_gasto)
            if not categoria_obj.exists():
                return Response(
                    {'message': f'No existe una categoría con Id={id_categoria} para este usuario.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            if not tipogasto_obj.exists():
                return Response(
                    {'message': f'No existe el tipo de gasto con Id={id_tipo_gasto}.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            data_registrar={
              'Id':0,
              'NombreGasto':nombre,
              'Observacion':observacion,
              'Usuario':id_usuario,
              'Categoria':id_categoria,
              'TipoGasto':id_tipo_gasto
            }
            serializer = RegistroGastoSerializer(data=data_registrar)
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
            
            gasto = serializer.save()
            detail_serializer = InfoGastoSerializer(gasto)
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ListarGastosUser(APIView):

    @AutenticacionToken
    def get(self, request, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')
            gastos_usuario=Gastos.objects.filter(Usuario_id=id_usuario)
            if not gastos_usuario.exists():
                return Response(
                    {'message': f'El usuario no tiene categorias registradas.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            detail_serializer = InfoGastoSerializer(gastos_usuario,many=True)
            return Response(detail_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from FinTrackApp.Decoradores.DecoradoresSeguridad import AutenticacionToken
from FinTrackApp.Modelos.CategoriasGastos import CategoriasGastos
from FinTrackApp.Serializadores.SerilizadoresModelos.CategoriaGastoSerializers import RegistroCategoriaGastoSerializer,InfoCategoriaGastoSerializer

class ListadoCageriasUser(APIView):
    @AutenticacionToken
    def get(self, request, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')
            categorias_usuario=CategoriasGastos.objects.filter(Usuario_id=id_usuario)
            if not categorias_usuario.exists():
                return Response(
                    {'message': f'El usuario no tiene categorias registradas.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            detail_serializer = InfoCategoriaGastoSerializer(categorias_usuario,many=True)
            return Response(detail_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CategoriaGastoUsuarioApi(APIView):

    @AutenticacionToken
    def post(self, request, *args, **kwargs):
        try:
            
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')

            nombre=request.data.get('nombre').strip()
            descripcion = request.data.get('descripcion', '').strip()
        
            data_registrar={
              'Id':0,
              'NombreCategoria':nombre,
              'Observacion':descripcion,
              'Usuario':id_usuario,
            }
            serializer = RegistroCategoriaGastoSerializer(data=data_registrar)
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
            detail_serializer = InfoCategoriaGastoSerializer(categoria)
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @AutenticacionToken
    def put(self, request, id_reg,*args, **kwargs):
        try:
            
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')

            nombre=request.data.get('nombre').strip()
            descripcion = request.data.get('descripcion', 'sin').strip()
            categoria_reg=CategoriasGastos.objects.filter(Id=id_reg,Usuario_id=id_usuario)
            if not categoria_reg.exists():
                return Response(
                    {'message': f'No existe una categoría con Id={id_reg} para este usuario.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            instancia_categoria=categoria_reg.first()
            data_registrar={
              'Id':id_reg,
              'NombreCategoria':nombre,
              'Observacion':descripcion,
              'Usuario':id_usuario,
            }
            serializer = RegistroCategoriaGastoSerializer(instance=instancia_categoria,data=data_registrar)
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
            detail_serializer = InfoCategoriaGastoSerializer(categoria)
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    @AutenticacionToken
    def delete(self, request, id_reg, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')
            categoria_reg=CategoriasGastos.objects.filter(Id=id_reg,Usuario_id=id_usuario)
            if not categoria_reg.exists():
                return Response(
                    {'message': f'No existe una categoría con Id={id_reg} para este usuario.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            instancia_categoria=categoria_reg.first()
            instancia_categoria.delete()
            return Response({'message':f'La categoria con id {id_reg} ha sido eliminada'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
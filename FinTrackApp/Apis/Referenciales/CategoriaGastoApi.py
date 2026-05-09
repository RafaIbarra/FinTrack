from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Sum, Count, Value, IntegerField, Q,Prefetch,DecimalField
from django.db.models.functions import Coalesce

from FinTrackApp.Decoradores.DecoradoresSeguridad import AutenticacionToken

from FinTrackApp.Modelos.CategoriasGastos import CategoriasGastos
from FinTrackApp.Modelos.Gastos import Gastos


from FinTrackApp.Serializadores.SerilizadoresModelos.CategoriaGastoSerializers import RegistroCategoriaGastoSerializer,InfoCategoriaGastoSerializer

class ListadoCategoriasUser(APIView):
    @AutenticacionToken
    def get(self, request, id_reg,*args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')
             # Query de gastos con agregados (para el Prefetch)
            
            gastos_qs = Gastos.objects.filter(
                Usuario_id=id_usuario
            ).annotate(
                TotalConcepto=Coalesce(
                    Sum(
                        'movimiento_gasto_seleccionado__MontoGasto',
                        filter=Q(
                            movimiento_gasto_seleccionado__MovimientoGasto__Usuario_id=id_usuario
                        ),
                        output_field=IntegerField()
                    ),
                    Value(0, output_field=IntegerField())
                ),
                CantidadRegistrosConcepto=Count(
                    'movimiento_gasto_seleccionado',
                    filter=Q(
                        movimiento_gasto_seleccionado__MovimientoGasto__Usuario_id=id_usuario
                    )
                )
            )
            

            # Categorías con agregados y prefetch
            if id_reg==0:
                categorias = CategoriasGastos.objects.filter(
                    Usuario_id=id_usuario
                ).annotate(
                    TotalGastoCategoria=Coalesce(
                        Sum(
                            'categoria_gasto_usuario__movimiento_gasto_seleccionado__MontoGasto',
                            filter=Q(
                                categoria_gasto_usuario__movimiento_gasto_seleccionado__MovimientoGasto__Usuario_id=id_usuario
                            ),
                            output_field=IntegerField()
                        ),
                        Value(0, output_field=IntegerField())
                    ),
                    CantidadGastosCategoria=Count(
                        'categoria_gasto_usuario__movimiento_gasto_seleccionado',
                        filter=Q(
                            categoria_gasto_usuario__movimiento_gasto_seleccionado__MovimientoGasto__Usuario_id=id_usuario
                        )
                    ),
                    CantidadConceptoGastos=Count(
                        'categoria_gasto_usuario', 
                        distinct=True
                    )
                ).prefetch_related(
                    Prefetch('categoria_gasto_usuario', queryset=gastos_qs)
                )
            else:
                categorias = CategoriasGastos.objects.filter(
                    Usuario_id=id_usuario,Id=id_reg
                ).annotate(
                    TotalGastoCategoria=Coalesce(
                        Sum(
                            'categoria_gasto_usuario__movimiento_gasto_seleccionado__MontoGasto',
                            filter=Q(
                                categoria_gasto_usuario__movimiento_gasto_seleccionado__MovimientoGasto__Usuario_id=id_usuario
                            ),
                            output_field=IntegerField()
                        ),
                        Value(0, output_field=IntegerField())
                    ),
                    CantidadGastosCategoria=Count(
                        'categoria_gasto_usuario__movimiento_gasto_seleccionado',
                        filter=Q(
                            categoria_gasto_usuario__movimiento_gasto_seleccionado__MovimientoGasto__Usuario_id=id_usuario
                        )
                    ),
                    CantidadConceptoGastos=Count(
                        'categoria_gasto_usuario', 
                        distinct=True
                    )
                ).prefetch_related(
                    Prefetch('categoria_gasto_usuario', queryset=gastos_qs)
                )
            
             
            detail_serializer = InfoCategoriaGastoSerializer(categorias,many=True)
            detalle = detail_serializer.data
            total_general = sum(
                categoria.get('TotalGastoCategoria', 0) or 0 
                for categoria in detalle
            )
            cantidad_categorias = len(detalle)
            
            data={
                'detalle':detalle ,
                'resumen': {
                    'TotalGeneral': total_general,
                    'CantidadCategorias': cantidad_categorias,
                }
            }
            return Response(data, status=status.HTTP_200_OK)
            # return Response({'message':'No disponible'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OperacionesCategoriasGastosUser(APIView):

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
            
            return Response({'message':'Registro correcto de categoria'}, status=status.HTTP_201_CREATED)
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
            
            return Response({'message':'Actualizacion correcta de categoria'}, status=status.HTTP_200_OK)
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
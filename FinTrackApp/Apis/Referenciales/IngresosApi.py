from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Sum, Count, Value, IntegerField, Q
from django.db.models.functions import Coalesce

from FinTrackApp.Decoradores.DecoradoresSeguridad import AutenticacionToken

from FinTrackApp.Modelos.Ingresos import Ingresos
from FinTrackApp.Modelos.TiposIngresos import TiposIngresos

from FinTrackApp.Serializadores.SerilizadoresModelos.IngresosSerializers import RegistroIngresoSerializer,InfoIngresoSerializer

class OperacionesIngresoUser(APIView):

    @AutenticacionToken
    def post(self, request, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')

            nombre=request.data.get('nombre').strip()
            observacion = request.data.get('observacion', '').strip()
            id_tipo_ingreso=int(request.data.get('tipo_ingreso'))
    
            tipo_ingreso_obj=TiposIngresos.objects.filter(Id=id_tipo_ingreso)
            
            if not tipo_ingreso_obj.exists():
                return Response(
                    {'message': f'No existe el tipo de ingreso con Id={id_tipo_ingreso}.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            data_registrar={
              'NombreIngreso':nombre,
              'Observacion':observacion,
              'Usuario':id_usuario,
              'TipoIngreso':id_tipo_ingreso
            }
            
            serializer = RegistroIngresoSerializer(data=data_registrar)
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
            
            ingreso = serializer.save()
            
            return Response({'message':'Registro correcto'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @AutenticacionToken
    def put(self, request, idingreso,*args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')

            nombre=request.data.get('nombre').strip()
            observacion = request.data.get('observacion', '').strip()
            id_tipo_ingreso=int(request.data.get('tipo_ingreso'))
    
            tipo_ingreso_obj=TiposIngresos.objects.filter(Id=id_tipo_ingreso)
            
            if not tipo_ingreso_obj.exists():
                return Response(
                    {'message': f'No existe el tipo de ingreso con Id={id_tipo_ingreso}.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            

            ingreso_obj=Ingresos.objects.filter(Id=idingreso,Usuario_id=id_usuario)
               
            if not ingreso_obj.exists():
                return Response(
                    {'message': f'No existe un ingreso con Id={idingreso} para este usuario.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            
            instancia_ingreso=ingreso_obj.first()
            data_registrar={
              'Id':idingreso,
              'NombreIngreso':nombre,
              'Observacion':observacion,
              'Usuario':id_usuario,
              'TipoIngreso':id_tipo_ingreso
            }
            serializer = RegistroIngresoSerializer(instance=instancia_ingreso,data=data_registrar)
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
            
            ingreso = serializer.save()
            
            return Response({'message':'Registro actualizado'}, status=status.HTTP_200_OK)

        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @AutenticacionToken
    def delete(self, request, idingreso, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')
            ingreso_obj=Ingresos.objects.filter(Id=idingreso,Usuario_id=id_usuario)
            if not ingreso_obj.exists():
                return Response(
                    {'message': f'No existe un ingreso con Id={idingreso} para este usuario.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            instancia_ingreso=ingreso_obj.first()
            instancia_ingreso.delete()
            return Response({'message':f'El ingreso con id {idingreso} ha sido eliminada'}, status=status.HTTP_200_OK)

        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class ListarIngresosUser(APIView):

    @AutenticacionToken
    def get(self, request,id_reg, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')
            if id_reg==0:
                ingresos_usuario=Ingresos.objects.filter(Usuario_id=id_usuario).annotate(
                    TotalIngreso=Coalesce(
                        Sum(
                            'movimiento_ingreso_seleccionado__MontoIngreso',
                            filter=Q(
                                movimiento_ingreso_seleccionado__Usuario_id=id_usuario
                            ),
                            output_field=IntegerField()
                        ),
                        Value(0, output_field=IntegerField())
                    ),
                    CantidadConcepto=Count(
                        'movimiento_ingreso_seleccionado',
                        filter=Q(
                            movimiento_ingreso_seleccionado__Usuario_id=id_usuario
                        )
                    )
                )
            else:

                 ingresos_usuario=Ingresos.objects.filter(Usuario_id=id_usuario,Id=id_reg).annotate(
                    TotalIngreso=Coalesce(
                        Sum(
                            'movimiento_ingreso_seleccionado__MontoIngreso',
                            filter=Q(
                                movimiento_ingreso_seleccionado__Usuario_id=id_usuario
                            ),
                            output_field=IntegerField()
                        ),
                        Value(0, output_field=IntegerField())
                    ),
                    CantidadConcepto=Count(
                        'movimiento_ingreso_seleccionado',
                        filter=Q(
                            movimiento_ingreso_seleccionado__Usuario_id=id_usuario
                        )
                    )
                )

            # if not ingresos_usuario.exists():
            #     return Response(
            #         {'message': f'El usuario no tiene categorias registradas.'},
            #         status=status.HTTP_200_OK
            #     )
            detail_serializer = InfoIngresoSerializer(ingresos_usuario,many=True)
            detalle = detail_serializer.data
            total_general = sum(
                ingreso.get('TotalIngreso', 0) or 0 
                for ingreso in detalle
            )
            cantidad_medios = len(detalle)
            
            data={
                'detalle':detalle ,
                'resumen': {
                    'TotalGeneral': total_general,
                    'CantidadIngresos': cantidad_medios,
                }
            }
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
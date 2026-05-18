from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.permissions import AllowAny
from FinTrackApp.Serializadores.SerializadoresValidaciones.CamposRequeridosSerializers import LoginUsuarioInputSerializers
from FinTrackApp.Utils.funciones_seguridad import informacion_peticion,registrar_login
from FinTrackApp.Decoradores.DecoradoresSeguridad import AutenticacionToken
from FinTrackApp.Modelos.Usuarios import Usuarios
from FinTrackApp.Modelos.CategoriasGastos import CategoriasGastos
from FinTrackApp.Modelos.Gastos import Gastos
from FinTrackApp.Modelos.Ingresos import Ingresos
class LoginUsuario(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        try:
            input_serializer =LoginUsuarioInputSerializers(data=request.data)
            if not input_serializer.is_valid():
                return Response(
                    {'message': input_serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            validated_data = input_serializer.validated_data
            user_name = validated_data['user'].strip()
            password = validated_data['password']
            data_peticion=informacion_peticion(request)
            ip_peticion=data_peticion.get('Ip')
            dispositivo=data_peticion.get('Dispositivo')
            loguedo,data,mensaje,data_usuario=registrar_login(user_name,password,ip_peticion,dispositivo)
           
            if loguedo:
                # datauser=[{
                #             'username':data_usuario.UserName.capitalize(),
                #             'nombre':data_usuario.NombreUsuario,
                #             'apellido':data_usuario.ApellidoUsuario,
                #             'fecha_registro':data_usuario.FechaRegistro.strftime("%d/%m/%Y %H:%M:%S"),
                            
                #         }]
                recorrido=False
                if data_usuario[0]['Isadmin']:
                        recorrido=False
                else:
                    id_usuario=data_usuario[0]['UserId']
                    categorias = CategoriasGastos.objects.filter(Usuario_id=id_usuario)
                    gastos = Gastos.objects.filter(Usuario_id=id_usuario)
                    ingresos = Ingresos.objects.filter(Usuario_id=id_usuario)
                    data_recorrido={
                        'categoria':False,
                        'conceptos':False,
                        'ingresos':False
                    }
                    if categorias.exists() and gastos.exists() and ingresos.exists():
                        recorrido=False
                    else:
                        recorrido=True
                        if not categorias.exists():
                            data_recorrido['categoria'] = True

                        if not gastos.exists():
                            data_recorrido['conceptos'] = True

                        if not ingresos.exists():
                            data_recorrido['ingresos'] = True
                
                valores_logueo={
                    'Logueado':loguedo,
                    'token': data.get('token_jwt') if data else '',  # Puede ser None
                    'refresh': data.get('refresh_jwt') if data else '',  # Puede ser None
                    'sesion': data.get('token_clasico') if data else '',  # Puede ser None
                    'user_name': user_name.capitalize(),
                    'message':mensaje,
                    'datauser':data_usuario,
                    'recorrido':recorrido,
                    'datarecorrido':data_recorrido
                }
                
                
            
                return Response(valores_logueo, status=status.HTTP_200_OK)
            else:
                return Response({'message':mensaje}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class ComprobarSession(APIView):
    @AutenticacionToken
    def get(self, request, *args, **kwargs):
        try:
            user_info = getattr(request, 'user_info', {})
            user_login = user_info["username"]
            id_usuario=user_info.get('usuario_id')
            usuario_data=Usuarios.objects.filter(UserName=user_login).first()
            if not usuario_data:
                return Response(
                    {'message': f'Error de Usuario'},
                    status=status.HTTP_404_NOT_FOUND
                )
            recorrido=False
            categorias = CategoriasGastos.objects.filter(Usuario_id=id_usuario)
            gastos = Gastos.objects.filter(Usuario_id=id_usuario)
            ingresos = Ingresos.objects.filter(Usuario_id=id_usuario)
            data_recorrido={
                'categoria':False,
                'conceptos':False,
                'ingresos':False
            }
            if categorias.exists() and gastos.exists() and ingresos.exists():
                recorrido=False
            else:
                recorrido=True
                if not categorias.exists():
                    data_recorrido['categoria'] = True

                if not gastos.exists():
                    data_recorrido['conceptos'] = True

                if not ingresos.exists():
                    data_recorrido['ingresos'] = True
                
            datauser=[{
                            'username':usuario_data.UserName.capitalize(),
                            'nombre':usuario_data.NombreUsuario,
                            'apellido':usuario_data.ApellidoUsuario,
                            'fecha_registro':usuario_data.FechaRegistro.strftime("%d/%m/%Y %H:%M:%S"),
                            'recorrido':recorrido,
                            'datarecorrido':data_recorrido
                            
                        }]
            
            return Response(datauser, status=status.HTTP_200_OK)
            
        except Exception as e:
            
            return Response(
                 {'message': f'Error interno del servidor: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import authenticate
from FinTrackApp.Modelos.Usuarios import Usuarios
from FinTrackApp.Modelos.SesionesActivas import SesionesActivas
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from rest_framework.authtoken.models import Token
import re
def formato_user(data):
    """
    Tareas:\n
    * No puede contener espacios en blanco
    * No puede contener numeros
    * Debe estar todo en minusculas
    """
    data = data.replace(" ", "")
    data = data.lower()
    data = re.sub(r'[^a-zA-Z0-9]', '', data)
    return data

def informacion_peticion(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_peticion = x_forwarded_for.split(',')[0]
    else:
        ip_peticion = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    data={
        'Ip':ip_peticion,
        'Dispositivo':user_agent
    }
    return data

def registrar_login(usuario,contraseña,ip_peticion,user_agent):
    logueado=False 
    try:
        user = authenticate(username=usuario,password=contraseña)
        
        if user:
            usuario=Usuarios.objects.filter(UserName=usuario).first()
            valores=generar_sesion(usuario,ip_peticion,user_agent)
            logueado=valores.get('creado')
            msg=''
            if not logueado:
                msg=valores.get('error')
            
            return logueado,valores,msg
        else:
            logueado=False
            msg='Contraseña o nombre de usuario incorrectos'
            if  Usuarios.objects.filter(UserName=usuario).exists():
                msg='Contraseña incorrecta'
            return logueado,[], msg
    
    except Exception as e:
        # print(f"Error en generar_sesion: {str(e)}")
        return logueado,[], str(e)

def generar_sesion(usuario_obj,ip_peticion,user_agent):
    """
    usuario_obj: Instancia del modelo Usuarios
    password: Contraseña del usuario (para generar JWT)
    user_agent: String con información del dispositivo
    
    Retorna ambos tokens: token_clasico y token_jwt
    """
    resultado = {
        'creado': False,
        'token_clasico': None,
        'token_jwt': None,
        'refresh_jwt': None,
        'error': None
    }
    
    try:
        # 1. Eliminar sesiones anteriores del usuario
        SesionesActivas.objects.filter(Usuario=usuario_obj.Id).delete()
        
        # 2. BUSCAR usuario de Django por username
        user_django = User.objects.get(username=usuario_obj.UserName)

        
        
        # 4. GENERAR TOKEN JWT
        refresh = RefreshToken.for_user(user_django)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # 5. Calcular fecha de expiración
        tiempo_sesion = getattr(settings, 'TOKEN_SESION_TIEMPO', 8)
        fecha_expiracion = timezone.now() + timedelta(hours=tiempo_sesion)
        
        # token_clasic=generar_token_personalizado(usuario_obj,user_django,roles,fecha_expiracion)
        Token.objects.filter(user_id=user_django.id).delete()
        token,created= Token.objects.get_or_create(user=user_django)
        token_clasic=token.key
        # 6. Crear sesión DIRECTAMENTE con el modelo (sin serializador)
        SesionesActivas.objects.create(
            Usuario_id=usuario_obj.Id,
            IdDjangoUser=user_django.id,
            FechaExpiracion=fecha_expiracion,
            TokenSesion=token_clasic,
            FechaConexion=timezone.now(),
            Dispositivo=user_agent,
            IpConexion=ip_peticion
            # dispositivo ya no existe en el nuevo modelo
        )
        
        # 7. Retornar resultado exitoso con AMBOS tokens
        resultado['creado'] = True
        resultado['token_clasico'] = token_clasic
        resultado['token_jwt'] = access_token
        resultado['refresh_jwt'] = refresh_token
            
    except User.DoesNotExist:
        resultado['error'] = f"Usuario de Django no encontrado: {usuario_obj.UserName}"
    except Exception as e:
        # print(f"Error en generar_sesion: {str(e)}")
        resultado['error'] = str(e)
    
    return resultado

from functools import wraps
from django.http import JsonResponse
import jwt
from django.conf import settings

from django.utils import timezone
from FinTrackApp.Modelos.SesionesActivas import SesionesActivas


def AutenticacionToken(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        try:
            
            # 1. Extraer el header personalizado X-SESSION-USER (PRIMERO)
            x_session_user = request.META.get('HTTP_X_SESSION_USER')
            print(x_session_user)
            if not x_session_user:
                return JsonResponse({
                    'success': False,
                    'error': 'Token clásico requerido'
                }, status=401)
            
            # 2. CONSULTA BD: Verificar que el token existe en sesiones activas
            data_sesion=SesionesActivas.objects.filter(TokenSesion=x_session_user).first()
            if not data_sesion:
                return JsonResponse({
                    'success': False,
                    'error': 'Token inválido o sesión cerrada'
                }, status=401)
            
            # 3. Extraer el token JWT del request
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if not auth_header.startswith('Bearer '):
                return JsonResponse({
                    'success': False,
                    'error': 'Token JWT requerido'
                }, status=401)
            
            token = auth_header.split(' ')[1]
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"], options={"verify_signature": False})
            user_id_jwt = decoded_token.get('user_id')
            
            
            if str(user_id_jwt) != str(data_sesion.IdDjangoUser):
                return JsonResponse({
                    'success': False,
                    'error': 'User ID no coincide entre tokens'
                }, status=401)
            
            if timezone.now()> data_sesion.FechaExpiracion:
                return JsonResponse({
                    'success': False,
                    'error': 'Su sesion ha expirado'
                }, status=401)
            # # 6. AGREGAR INFORMACIÓN DEL USUARIO AL REQUEST
            request.user_info = {
                'usuario_id': data_sesion.Usuario.Id,
                'username': data_sesion.Usuario.UserName,
                # 'roles': classic_payload.get('roles', [])
            }
            
            # 7. Si pasa todas las validaciones, ejecutar el endpoint
            return view_func(self, request, *args, **kwargs)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error de validación: {str(e)}'
            }, status=500)
    _wrapped_view._tiene_autenticacion = True  # ← Necesario para validador
    return _wrapped_view



# utils/supabase_client.py
# PARCHER storage3 para eliminar warnnig Storage endpoint URL should have a trailing slash
import storage3._sync.bucket as storage_bucket_module

# Guardar el print original
original_print = print

# Crear un print filtrado
def filtered_print(*args, **kwargs):
    if args and "Storage endpoint URL should have a trailing slash" in str(args[0]):
        return  # No imprimir este mensaje
    original_print(*args, **kwargs)

# Aplicar el parche
import builtins
builtins.print = filtered_print




import os
from supabase import create_client, Client
from django.conf import settings

class SupabaseStorage:
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_SERVICE_KEY
        self.client: Client = create_client(self.url, self.key)
        
        # Crear bucket automáticamente
        self.crear_bucket_gastos()
    
    def crear_bucket_gastos(self):
        """Crea el bucket 'gastos_img' si no existe"""
        try:
            self.client.storage.create_bucket(
                id='gastos_img',
                name='gastos_img',
                options={"public": True}
            )
            # print("✅ Bucket 'productos' creado")
        except Exception as e:
            if "already exists" in str(e):
                pass
                # print("ℹ️ Bucket 'productos' ya existe")
            else:
                print(f"⚠️ Error: {e}")
    
    def upload_product_image(self, file_bytes: bytes, file_name: str):
        """Sube imagen de producto y retorna URL"""
        # Crear path único
        try:
            from datetime import datetime
            import uuid
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = uuid.uuid4().hex[:8]
            ext = os.path.splitext(file_name)[1] or '.jpg'
            if settings.DEBUG:
                timestamp=f'FIND_{timestamp}'
            path = f"imagenes/{timestamp}_{unique_id}{ext}"
            
            # Subir imagen
            print("asdasd")
            response = self.client.storage.from_('gastos_img').upload(
                path=path,
                file=file_bytes,
                file_options={"content-type": "image/jpeg"}
            )
            print("despues")
            # Obtener URL pública
            url = self.client.storage.from_('gastos_img').get_public_url(path)
            
            return {
                'success': True,
                'url': url,
                'path': path,
                'message':'OK'
            }
        except Exception as e:
            return {
                'success': False,
                'url': '',
                'path': '',
                'message':{str(e)}
            }
            
    
    def delete_product_image(self, image_url: str):
        """Elimina imagen usando su URL - Retorna True/False con detalles"""
        try:
            if not image_url:
                return {'success': True, 'message': 'No hay imagen para eliminar'}
            
            # Verificar que sea una URL de Supabase válida
            if not image_url.startswith('https://'):
                return {
                    'success': False, 
                    'error': 'URL inválida',
                    'details': 'La URL no comienza con https://'
                }
            
            # Extraer path de la URL de Supabase
            # Ejemplo: https://xxxxx.supabase.co/storage/v1/object/public/productos/imagenes/archivo.jpg
            import re
            import urllib.parse
            
            # Patrón para extraer el path después de 'public/productos/'
            pattern = r'/public/gastos_img/(.+)'
            match = re.search(pattern, image_url)
            
            if not match:
                return {
                    'success': False,
                    'error': 'URL no corresponde a bucket de productos',
                    'details': f'URL no contiene /public/gastos_img/: {image_url}'
                }
            
            path = match.group(1)
            # Decodificar URL si está codificada
            path = urllib.parse.unquote(path)
            
            
            
            # Eliminar del bucket 'productos'
            try:
                response = self.client.storage.from_('gastos_img').remove([path])
                
                return {'success': True, 'path': path}
                
            except Exception as remove_error:
                # Verificar si el error es que el archivo ya no existe
                error_msg = str(remove_error)
                if "not found" in error_msg.lower() or "no such file" in error_msg.lower():
                    
                    return {'success': True, 'message': 'Imagen ya no existe en el bucket'}
                else:
                    raise remove_error  # Relanzar otros errores
                
        except Exception as e:
            error_msg = str(e)
            return {
                'success': False,
                'error': 'Error eliminando imagen',
                'details': error_msg,
                'image_url': image_url
            }

# Instancia global
supabase_storage = SupabaseStorage()
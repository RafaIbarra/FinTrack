# utils/r2_storage.py
import os
import re
import uuid
import urllib.parse
from datetime import datetime
from io import BytesIO

import boto3
from botocore.exceptions import ClientError
from django.conf import settings


class R2Storage:
    """
    Cliente de almacenamiento para Cloudflare R2 (API S3-compatible).
    Reemplazo directo de SupabaseStorage.
    """

    # Buckets
    BUCKET_GASTOS = 'gastos-img'
    BUCKET_INGRESOS = 'ingresos-img'
    BUCKET_LOGO_EMPRESAS = 'logo-empresas'

    def __init__(self):
        # Configuración S3 API
        self.account_id = getattr(settings, 'R2_ACCOUNT_ID', '')
        self.access_key = getattr(settings, 'R2_ACCESS_KEY_ID', '')
        self.secret_key = getattr(settings, 'R2_SECRET_ACCESS_KEY', '')
        self.endpoint_url = getattr(settings, 'R2_ENDPOINT_URL', '')

        # URLs públicas por bucket
        self.public_urls = {
            self.BUCKET_GASTOS: getattr(settings, 'R2_PUBLIC_URL_GASTOS', ''),
            self.BUCKET_INGRESOS: getattr(settings, 'R2_PUBLIC_URL_INGRESOS', ''),
            self.BUCKET_LOGO_EMPRESAS: getattr(settings, 'R2_PUBLIC_URL_LOGO_EMPRESAS', ''),
        }

        if not all([self.account_id, self.access_key, self.secret_key, self.endpoint_url]):
            raise ValueError(
                "Faltan credenciales de R2 en settings. "
                "Requeridas: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_ENDPOINT_URL"
            )

        self.client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name='auto'
        )

        # Crear buckets automáticamente
        self._crear_bucket_si_no_existe(self.BUCKET_GASTOS)
        self._crear_bucket_si_no_existe(self.BUCKET_INGRESOS)
        self._crear_bucket_si_no_existe(self.BUCKET_LOGO_EMPRESAS)

    def _crear_bucket_si_no_existe(self, bucket_name):
        """Crea el bucket si no existe."""
        try:
            self.client.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ('404', 'NoSuchBucket', 'NotFound'):
                try:
                    self.client.create_bucket(Bucket=bucket_name)
                    print(f"✅ Bucket '{bucket_name}' creado")
                except Exception as create_err:
                    print(f"⚠️ Error creando bucket '{bucket_name}': {create_err}")
            else:
                print(f"⚠️ Error verificando bucket '{bucket_name}': {e}")

    # ───────────────────────────────────────────────
    # GASTOS
    # ───────────────────────────────────────────────

    def upload_gasto_image(self, file_bytes: bytes, file_name: str):
        return self._upload_image(self.BUCKET_GASTOS, file_bytes, file_name)

    def delete_gasto_image(self, image_url: str):
        return self._delete_image(self.BUCKET_GASTOS, image_url)

    # ───────────────────────────────────────────────
    # INGRESOS
    # ───────────────────────────────────────────────

    def upload_ingreso_image(self, file_bytes: bytes, file_name: str):
        return self._upload_image(self.BUCKET_INGRESOS, file_bytes, file_name)

    def delete_ingreso_image(self, image_url: str):
        return self._delete_image(self.BUCKET_INGRESOS, image_url)

    # ───────────────────────────────────────────────
    # LOGO EMPRESAS
    # ───────────────────────────────────────────────

    def upload_logo_empresa(self, file_bytes: bytes, file_name: str):
        return self._upload_image(self.BUCKET_LOGO_EMPRESAS, file_bytes, file_name)

    def delete_logo_empresa(self, image_url: str):
        return self._delete_image(self.BUCKET_LOGO_EMPRESAS, image_url)

    # ───────────────────────────────────────────────
    # MÉTODOS INTERNOS
    # ───────────────────────────────────────────────

    def _generar_path(self, file_name: str) -> str:
        """Genera path único: imagenes/20260518_210200_a1b2c3d4.jpg"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4().hex[:8]
        ext = os.path.splitext(file_name)[1] or '.jpg'

        if settings.DEBUG:
            timestamp = f'FIND_{timestamp}'

        return f"imagenes/{timestamp}_{unique_id}{ext}"

    def _upload_image(self, bucket: str, file_bytes: bytes, file_name: str):
        """Subida central."""
        try:
            path = self._generar_path(file_name)

            ext = os.path.splitext(file_name)[1].lower()
            content_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
                '.svg': 'image/svg+xml',
            }.get(ext, 'image/jpeg')

            self.client.put_object(
                Bucket=bucket,
                Key=path,
                Body=BytesIO(file_bytes),
                ContentType=content_type
            )

            url = self._construir_url_publica(bucket, path)

            return {
                'success': True,
                'url': url,
                'path': path,
                'message': 'OK'
            }

        except Exception as e:
            return {
                'success': False,
                'url': '',
                'path': '',
                'message': str(e)
            }

    def _delete_image(self, bucket: str, image_url: str):
        """Eliminación central."""
        try:
            if not image_url:
                return {'success': True, 'message': 'No hay imagen para eliminar'}

            path = self._extraer_path_de_url(image_url, bucket)

            if not path:
                return {
                    'success': False,
                    'error': 'URL no corresponde al bucket',
                    'details': f'No se pudo extraer path de: {image_url}'
                }

            self.client.delete_object(Bucket=bucket, Key=path)

            return {'success': True, 'path': path}

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ('NoSuchKey', '404'):
                return {'success': True, 'message': 'Imagen ya no existe en el bucket'}
            return {
                'success': False,
                'error': 'Error eliminando imagen',
                'details': str(e),
                'image_url': image_url
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Error eliminando imagen',
                'details': str(e),
                'image_url': image_url
            }

    def _construir_url_publica(self, bucket: str, path: str) -> str:
        """
        Construye URL pública.
        Usa la URL pública específica del bucket (sin incluir el nombre del bucket en la ruta).
        """
        public_url = self.public_urls.get(bucket, '')

        if public_url:
            # URL pública de R2: https://pub-xxx.r2.dev/imagenes/archivo.png
            return f"{public_url.rstrip('/')}/{path}"

        # Fallback: endpoint S3 nativo (requiere firma, no es público)
        return f"{self.endpoint_url}/{bucket}/{path}"

    def _extraer_path_de_url(self, image_url: str, bucket: str) -> str | None:
        """Extrae el path (Key) de una URL de R2."""
        if not image_url.startswith('https://'):
            return None

        # Patrón 1: URL nativa R2 (endpoint S3)
        pattern_nativa = rf'https://[^/]+\.r2\.cloudflarestorage\.com/{re.escape(bucket)}/(.+)'
        match = re.search(pattern_nativa, image_url)
        if match:
            return urllib.parse.unquote(match.group(1))

        # Patrón 2: URL pública del bucket (sin nombre de bucket en ruta)
        public_url = self.public_urls.get(bucket, '')
        if public_url:
            pattern_public = rf'{re.escape(public_url.rstrip("/"))}/(.+)'
            match = re.search(pattern_public, image_url)
            if match:
                return urllib.parse.unquote(match.group(1))

        # Patrón 3: Fallback genérico - buscar después del bucket en cualquier URL
        pattern_generico = rf'/{re.escape(bucket)}/(.+)'
        match = re.search(pattern_generico, image_url)
        if match:
            return urllib.parse.unquote(match.group(1))

        return None


# Instancia global
r2_storage = R2Storage()
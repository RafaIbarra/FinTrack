import csv
import os
import re
from django.conf import settings
from FinTrackApp.Modelos.Empresas import Empresas
from FinTrackApp.Utils.r2_storage import r2_storage


def formatear_ruc(ruc):
    """Convierte 80000084 en 8000008-4"""
    ruc_str = str(ruc).strip()
    if len(ruc_str) > 1:
        return f"{ruc_str[:-1]}-{ruc_str[-1]}"
    return ruc_str


def buscar_logo_por_id_fila(id_fila, logos_origen):
    """
    Busca en la carpeta logos un archivo cuyo nombre empiece con 'id_fila_'.
    Retorna la ruta completa si encuentra, None si no.
    """
    # Convertir id_fila a string para comparar
    id_str = str(id_fila).strip()

    # Patrón: ^id_fila_ (al inicio del nombre)
    patron = re.compile(rf'^{re.escape(id_str)}_.+')

    for nombre_archivo in os.listdir(logos_origen):
        if patron.match(nombre_archivo):
            return os.path.join(logos_origen, nombre_archivo)

    return None


def importar_empresas_desde_csv():
    # Rutas
    base_dir = settings.BASE_DIR
    csv_path = os.path.join(base_dir, 'CreacionEmpresas', 'resultados.csv')
    logos_origen = os.path.join(base_dir, 'CreacionEmpresas', 'logos')

    # Verificar que existan las rutas
    if not os.path.exists(csv_path):
        print(f"✗ No existe el archivo CSV: {csv_path}")
        return

    if not os.path.exists(logos_origen):
        print(f"✗ No existe la carpeta de logos: {logos_origen}")
        return

    # PASO 1: Crear o obtener la empresa "Indefinida"
    empresa_indefinida, creada = Empresas.objects.get_or_create(
        Ruc='',  # Identificar por RUC vacío
        defaults={
            'NombreEmpresa': 'Indefinida',
            'UrlImg': None
        }
    )

    if creada:
        print(f"✓ Empresa 'Indefinida' creada con ID: {empresa_indefinida.Id}")
    else:
        print(f"✓ Empresa 'Indefinida' ya existe con ID: {empresa_indefinida.Id}")

    # PASO 2: Leer el CSV y registrar las demás empresas
    with open(csv_path, 'r', encoding='utf-8-sig') as archivo_csv:
        lector = csv.DictReader(archivo_csv, delimiter=';')

        registrados = 0
        con_logo = 0
        sin_logo = 0
        errores_logo = 0

        for fila in lector:
            id_fila = fila.get('id_fila', '').strip()
            ruc_original = fila.get('ruc', '').strip()
            nombre_empresa = fila.get('nombre_empresa', '').strip()

            if not ruc_original or not nombre_empresa:
                print(f"Saltando fila sin RUC o nombre: id_fila={id_fila}")
                continue

            ruc_formateado = formatear_ruc(ruc_original)

            # Evitar duplicados por RUC
            empresa, creada = Empresas.objects.get_or_create(
                Ruc=ruc_formateado,
                defaults={
                    'NombreEmpresa': nombre_empresa,
                    'UrlImg': None
                }
            )

            if not creada:
                print(f"Actualizando empresa existente: {ruc_formateado} - {nombre_empresa}")
                empresa.NombreEmpresa = nombre_empresa
            else:
                print(f"Creando nueva empresa: {nombre_empresa} | RUC: {ruc_formateado}")

            # Buscar logo por id_fila
            ruta_logo = buscar_logo_por_id_fila(id_fila, logos_origen)

            if ruta_logo:
                nombre_archivo = os.path.basename(ruta_logo)
                print(f"  → Logo encontrado: {nombre_archivo}")

                try:
                    with open(ruta_logo, 'rb') as img_file:
                        file_bytes = img_file.read()

                    # Subir a R2
                    resultado = r2_storage.upload_logo_empresa(
                        file_bytes=file_bytes,
                        file_name=nombre_archivo
                    )

                    if resultado['success']:
                        empresa.UrlImg = resultado['url']
                        print(f"  ✓ Logo subido a R2: {resultado['url']}")
                        con_logo += 1
                    else:
                        print(f"  ✗ Error subiendo logo a R2: {resultado['message']}")
                        empresa.UrlImg = None
                        errores_logo += 1

                except Exception as e:
                    print(f"  ✗ Error leyendo o subiendo logo: {str(e)}")
                    empresa.UrlImg = None
                    errores_logo += 1
            else:
                empresa.UrlImg = None
                print(f"  - Sin logo (id_fila={id_fila} no encontrado en logos)")
                sin_logo += 1

            empresa.save()
            registrados += 1
            print(f"  Empresa: {nombre_empresa} | RUC: {ruc_formateado} | ID: {empresa.Id}")

    print(f"\n--- RESUMEN ---")
    print(f"Empresa Indefinida: ID={empresa_indefinida.Id} (Ruc='')")
    print(f"Total procesadas del CSV: {registrados}")
    print(f"Con logo subido a R2: {con_logo}")
    print(f"Sin logo: {sin_logo}")
    print(f"Errores al subir logo: {errores_logo}")
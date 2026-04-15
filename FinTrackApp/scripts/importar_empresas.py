import csv
import os
from django.core.files import File
from django.conf import settings
from django.db import connection
from FinTrackApp.models import Empresas

def formatear_ruc(ruc):
    """Convierte 80000084 en 8000008-4"""
    ruc_str = str(ruc).strip()
    if len(ruc_str) > 1:
        return f"{ruc_str[:-1]}-{ruc_str[-1]}"
    return ruc_str

def importar_empresas_desde_csv():
    # Rutas
    base_dir = settings.BASE_DIR
    csv_path = os.path.join(base_dir, 'CreacionEmpresas', 'resultados.csv')
    logos_origen = os.path.join(base_dir, 'CreacionEmpresas', 'logos')
    
    # PASO 1: Crear o obtener la empresa "Indefinida" (SIN forzar ID)
    empresa_indefinida, creada = Empresas.objects.get_or_create(
        Ruc='',  # Identificar por RUC vacío
        NombreEmpresa='Indefinida',  # También por nombre
        defaults={
            'UrlImg': None,
            'ObsImg': 'Empresa por defecto para registros sin asignar'
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
        
        for fila in lector:
            ruc_original = fila.get('ruc', '').strip()
            nombre_empresa = fila.get('nombre_empresa', '').strip()
            status = fila.get('status', '').strip()
            ruta_completa = fila.get('ruta_completa', '').strip()
            
            if not ruc_original or not nombre_empresa:
                print(f"Saltando fila sin RUC o nombre: {fila}")
                continue
            
            ruc_formateado = formatear_ruc(ruc_original)
            
            # Evitar duplicados
            empresa, creada = Empresas.objects.get_or_create(
                Ruc=ruc_formateado,
                defaults={
                    'NombreEmpresa': nombre_empresa,
                    'ObsImg': f"Importado desde CSV. Status original: {status}"
                }
            )
            
            if not creada:
                print(f"Actualizando empresa existente: {ruc_formateado}")
                empresa.NombreEmpresa = nombre_empresa
            
            if status == 'OK' and ruta_completa:
                nombre_archivo = os.path.basename(ruta_completa)
                ruta_imagen = os.path.join(logos_origen, nombre_archivo)
                
                if os.path.exists(ruta_imagen):
                    with open(ruta_imagen, 'rb') as img_file:
                        django_file = File(img_file, name=nombre_archivo)
                        empresa.UrlImg.save(nombre_archivo, django_file, save=False)
                    print(f"  ✓ Logo agregado: {nombre_archivo}")
                    con_logo += 1
                else:
                    print(f"  ✗ Logo no encontrado: {ruta_imagen}")
                    empresa.ObsImg = f"{empresa.ObsImg} | Logo faltante: {nombre_archivo}"
                    sin_logo += 1
            else:
                empresa.UrlImg = None
                print(f"  - Registro sin logo (status: {status})")
                sin_logo += 1
            
            empresa.save()
            registrados += 1
            print(f"  Empresa: {nombre_empresa} | RUC: {ruc_formateado} | ID: {empresa.Id}")
    
    print(f"\n--- RESUMEN ---")
    print(f"Empresa Indefinida: ID={empresa_indefinida.Id} (Ruc='')")
    print(f"Total procesadas del CSV: {registrados}")
    print(f"Con logo: {con_logo}")
    print(f"Sin logo: {sin_logo}")
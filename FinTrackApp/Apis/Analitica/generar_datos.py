from datetime import datetime, timedelta
from collections import defaultdict


def resumen_gastos_por_semana(detalle_gastos, anno, mes,total):
    """
    Calcula el total gastado por semana del mes.
    La semana inicia el DOMINGO.
    
    Args:
        detalle_gastos: Lista de gastos del serializer (formato dd/mm/yyyy)
        anno: Año del reporte
        mes: Mes del reporte (1-12)
    
    Returns:
        Lista de diccionarios con:
        - numero_semana: int
        - fecha_inicio: str (dd/mm/yyyy)
        - fecha_fin: str (dd/mm/yyyy)  
        - total: int (suma de TotalMovimiento)
        - cantidad_gastos: int (cantidad de movimientos)
        - dias_con_gastos: list (detalle por día con gastos)
    """
    
    # --- 1. Agrupar gastos por fecha ---
    gastos_por_fecha = defaultdict(lambda: {"total": 0, "cantidad": 0})
    
    for gasto in detalle_gastos:
        fecha = datetime.strptime(gasto['FechaGasto'], "%d/%m/%Y").date()
        
        # Solo gastos del mes/año solicitado
        if fecha.year == anno and fecha.month == mes:
            gastos_por_fecha[fecha]["total"] += gasto['TotalMovimiento']
            gastos_por_fecha[fecha]["cantidad"] += 1
    
    if not gastos_por_fecha:
        return []
    
    # --- 2. Calcular límites del mes ---
    primer_dia_mes = datetime(anno, mes, 1).date()
    if mes == 12:
        ultimo_dia_mes = datetime(anno + 1, 1, 1).date() - timedelta(days=1)
    else:
        ultimo_dia_mes = datetime(anno, mes + 1, 1).date() - timedelta(days=1)
    
    # --- 3. Encontrar el domingo de inicio de la primera semana ---
    # weekday(): Lunes=0, ..., Domingo=6
    if primer_dia_mes.weekday() == 6:  # El 1ro del mes es domingo
        inicio_primera_semana = primer_dia_mes
    else:
        # Retroceder hasta el domingo anterior
        inicio_primera_semana = primer_dia_mes - timedelta(days=primer_dia_mes.weekday() + 1)
    
    # --- 4. Generar todas las semanas ---
    semanas = []
    fecha_actual = inicio_primera_semana
    numero_semana = 1
    
    while fecha_actual <= ultimo_dia_mes:
        fin_semana = fecha_actual + timedelta(days=6)
        
        # Solo incluir semanas que tengan al menos un día del mes
        tiene_dia_del_mes = any(
            (fecha_actual + timedelta(days=d)).month == mes
            for d in range(7)
        )
        
        if tiene_dia_del_mes:
            # Calcular totales de la semana
            total_semana = 0
            cantidad_gastos = 0
            dias_detalle = []
            
            dia = fecha_actual
            while dia <= fin_semana:
                if dia in gastos_por_fecha:
                    info = gastos_por_fecha[dia]
                    total_semana += info["total"]
                    cantidad_gastos += info["cantidad"]
                    dias_detalle.append({
                        "fecha": dia.strftime("%d/%m/%Y"),
                        "total": info["total"],
                        "cantidad": info["cantidad"]
                    })
                dia += timedelta(days=1)

            leyenda_dia_inicio=fecha_actual.day if fecha_actual.day >9 else f'0{fecha_actual.day}'
            leyenda_mes_inicio=fecha_actual.month if fecha_actual.month >9 else f'0{fecha_actual.month}'

            leyenda_dia_fin=fin_semana.day if fin_semana.day >9 else f'0{fin_semana.day}'
            leyenda_mes_fin=fin_semana.month if fin_semana.month >9 else f'0{fin_semana.month}'
            if total_semana >0:
                porcentaje_semana=round((total_semana / total * 100), 2)
            else:
                porcentaje_semana=0.0

            semanas.append({
                "NumeroSemana": numero_semana,
                "FechaInicio": fecha_actual.strftime("%d/%m/%Y"),
                "FechaFin": fin_semana.strftime("%d/%m/%Y"),
                "Leyenda":f'{leyenda_dia_inicio}/{leyenda_mes_inicio} al {leyenda_dia_fin}/{leyenda_mes_fin}'  ,
                "TotalSemana": total_semana,
                "Porcentaje":porcentaje_semana,
                "CantidadGastos": cantidad_gastos,
                "DiasGasto": dias_detalle
            })
            numero_semana += 1
        
        fecha_actual = fin_semana + timedelta(days=1)
    
    return semanas

def resumen_gastos( detalle_gastos):

        # ========== RESULTADO DEL MES ==========
        total_egresos = sum(g['TotalMovimiento'] for g in detalle_gastos)
        cantidad_egresos = len(detalle_gastos)
        

        resultado_mes = {
            "TotalGasto": total_egresos,
            "cantidadGasto": cantidad_egresos,
            
        }

        # ========== GASTOS POR CATEGORÍA ==========
        categorias = {}
        for gasto in detalle_gastos:
            for detalle in gasto.get('DetalleGastos', []):
                cat = detalle['NombreCategoriaGasto']
                if cat not in categorias:
                    categorias[cat] = {"total": 0, "cantidad": 0}
                categorias[cat]["total"] += detalle['MontoGasto']
                categorias[cat]["cantidad"] += 1

        resumen_gastos_categoria = [
            {
                "CategoriaGasto": cat,
                "TotalCategoria": v["total"],
                "Cantidad": v["cantidad"],
                "Porcentaje": round(
                    (v["total"] / total_egresos * 100), 2
                ) if total_egresos > 0 else 0
            }
            for cat, v in categorias.items()
        ]

        # ========== GASTOS POR NOMBRE (NUEVO) ==========
        nombres_gasto = {}
        for gasto in detalle_gastos:
            for detalle in gasto.get('DetalleGastos', []):
                nombre = detalle['NombreGasto']
                if nombre not in nombres_gasto:
                    nombres_gasto[nombre] = {"total": 0, "cantidad": 0}
                nombres_gasto[nombre]["total"] += detalle['MontoGasto']
                nombres_gasto[nombre]["cantidad"] += 1

        resumen_gastos_nombre = [
            {
                "ConceptGasto": nombre,
                "TotalConcepto": v["total"],
                "CantidadConcepto": v["cantidad"],
                "Porcentaje": round(
                    (v["total"] / total_egresos * 100), 2
                ) if total_egresos > 0 else 0
            }
            for nombre, v in nombres_gasto.items()
        ]

      

        # ========== MEDIOS DE PAGO ==========
        medios = {}
        for gasto in detalle_gastos:
            for medio in gasto.get('DetalleMediosPagos', []):
                nombre = medio['NombreMedioPago']
                if nombre not in medios:
                    medios[nombre] = {"total": 0, "cantidad": 0}
                medios[nombre]["total"] += medio['MontoMedioPago']
                medios[nombre]["cantidad"] += 1

        resumen_medios = [
            {
                "MedioPago": nombre,
                "TotalMedioPago": v["total"],
                "Cantidad": v["cantidad"],
                "Porcentaje": round(
                    (v["total"] / total_egresos * 100), 2
                ) if total_egresos > 0 else 0
            }
            for nombre, v in medios.items()
        ]

        return {
            "TotalesGastos": resultado_mes,
            "GastosPorCategoria": resumen_gastos_categoria,
            "ResumenConceptosGastos":resumen_gastos_nombre,
            "ResumenPorMediosDePagos": resumen_medios
        }

def resumen_ingresos( detalle_ingresos):
    # ========== RESULTADO DEL MES ==========
        
        total_ingresos = sum(i['MontoIngreso'] for i in detalle_ingresos)
        cantidad_ingresos = len(detalle_ingresos)

        resultado_mes = {
            
            "TotalIngreso": total_ingresos,
            "CantidadIngreso": cantidad_ingresos,
            
        }

      
      

      

        # ========== INGRESOS ==========
        tipos = {}
        for ingreso in detalle_ingresos:
            tipo = ingreso['NombreIngreso']
            if tipo not in tipos:
                tipos[tipo] = {"total": 0, "cantidad": 0}
            tipos[tipo]["total"] += ingreso['MontoIngreso']
            tipos[tipo]["cantidad"] += 1

        resumen_ingresos = [
            {
                "NombreIngreso": tipo,
                "TotalIngreso": v["total"],
                "Cantidad": v["cantidad"],
                "Porcentaje": round(
                    (v["total"] / total_ingresos * 100), 2
                ) if total_ingresos > 0 else 0
            }
            for tipo, v in tipos.items()
        ]

       

        return {
            "TotalesIngresos": resultado_mes,
            "ConceptoIngresos": resumen_ingresos
            
        }